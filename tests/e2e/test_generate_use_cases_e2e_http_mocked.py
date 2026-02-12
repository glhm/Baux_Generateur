import os
import sys
import types
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# Provide lightweight stubs for optional google modules so imports work in test env.
if "googleapiclient" not in sys.modules:
    googleapiclient = types.ModuleType("googleapiclient")
    discovery = types.ModuleType("googleapiclient.discovery")
    http = types.ModuleType("googleapiclient.http")
    errors = types.ModuleType("googleapiclient.errors")

    discovery.build = MagicMock()

    class _DummyDownload:
        def __init__(self, *args, **kwargs):
            pass

        def next_chunk(self):
            return MagicMock(progress=lambda: 1.0), True

    class _DummyUpload:
        def __init__(self, *args, **kwargs):
            pass

    http.MediaIoBaseDownload = _DummyDownload
    http.MediaIoBaseUpload = _DummyUpload

    class _DummyHttpError(Exception):
        pass

    errors.HttpError = _DummyHttpError

    sys.modules["googleapiclient"] = googleapiclient
    sys.modules["googleapiclient.discovery"] = discovery
    sys.modules["googleapiclient.http"] = http
    sys.modules["googleapiclient.errors"] = errors


if "google_auth_oauthlib.flow" not in sys.modules:
    ga_module = types.ModuleType("google_auth_oauthlib")
    flow_module = types.ModuleType("google_auth_oauthlib.flow")

    class _DummyInstalledAppFlow:
        @staticmethod
        def from_client_config(*args, **kwargs):
            class _Flow:
                def run_local_server(self, port=0):
                    return MagicMock(valid=True)

            return _Flow()

    flow_module.InstalledAppFlow = _DummyInstalledAppFlow
    sys.modules["google_auth_oauthlib"] = ga_module
    sys.modules["google_auth_oauthlib.flow"] = flow_module

if "google.auth.transport.requests" not in sys.modules:
    google_module = types.ModuleType("google")
    auth_module = types.ModuleType("google.auth")
    transport_module = types.ModuleType("google.auth.transport")
    requests_module = types.ModuleType("google.auth.transport.requests")

    class _DummyRequest:
        pass

    requests_module.Request = _DummyRequest
    sys.modules["google"] = google_module
    sys.modules["google.auth"] = auth_module
    sys.modules["google.auth.transport"] = transport_module
    sys.modules["google.auth.transport.requests"] = requests_module

if "src.domain.housing_strings" not in sys.modules:
    housing_strings = types.ModuleType("src.domain.housing_strings")
    housing_strings.cautionnement_physique = ""
    housing_strings.la_caution_physique = ""
    housing_strings.signature_des_garants = ""
    housing_strings.cautionnement_visale = ""
    housing_strings.doc_visale = ""
    housing_strings.bail_meuble_duree = ""
    housing_strings.reconduction_meuble = ""
    housing_strings.duree_contrat_meuble = ""
    housing_strings.bail_etudiant_titre = ""
    housing_strings.bail_etudiant_duree = ""
    housing_strings.duree_contrat_etudiant = ""
    sys.modules["src.domain.housing_strings"] = housing_strings

from src.conf.info_apis import CAUTION_ID, ID_TEMPLATE_BAIL_MEUBLE, MAP_PAGE_NOTION_BIEN_TO_REPO, TEMPLATE_QUITTANCE_ID
from src.domain.entities.financials import Financials
from src.domain.entities.guarantor import PhysicalGuarantor, VisaleGuarantor
from src.domain.entities.lease import Lease
from src.domain.entities.property import Property
from src.domain.entities.room import Room
from src.domain.entities.tenant import Tenant
from src.domain.entities.value_objects import Period
from src.use_cases.generate_lease_use_case import GenerateLeaseUseCase
from src.use_cases.generate_receipt_use_case import GenerateReceiptUseCase


def _make_property(mapped_id: str):
    return Property(
        id=mapped_id,
        address="55 Rue Renée Auduc, 94000 Créteil",
        owner_name="SCI Immobilière",
        owner_address="10 Rue du Commerce, 75015 Paris",
        surface_habitable="120",
        numero_dpe="DPE-123",
        autres_parties="N/A",
        date_construction=1985,
        designation="Appartement",
        classe_dpe="C",
        elements_equipement="Cuisine équipée",
        enumeration_contenu="Lit, Bureau",
        modalite_chauffage="Collectif",
        modalite_eau="Collective",
        nombre_pieces=5,
        regime_juridique="Monopropriété",
        type_habitat="Collectif",
    )


def _make_room():
    return Room(name="Chambre 1", localisation="2ème étage", surface=12.0, volume="Standard")


def _make_tenant(years, gen_lease=True, gen_receipt=True):
    return Tenant(
        nom="Dupont Jean",
        email="jean.dupont@email.com",
        date_naissance="15/03/1995",
        lieu_naissance="Paris",
        envoyer_quittance=False,
        activer_generation=gen_lease,
        activer_generation_quittances=gen_receipt,
        statut_envoi_quittance="Reinit",
        years=years,
    )


def _make_lease(guarantor, start_date: date, end_date: date | None, years):
    financials = Financials.calculate(
        loyer_amount=450,
        charges_amount=50,
        jour_arrivee=start_date.day,
        mois_arrivee_str="Janvier",
        year=start_date.year,
    )
    mapped_property_id = list(MAP_PAGE_NOTION_BIEN_TO_REPO.keys())[0]
    return Lease(
        id="lease-page-id-123",
        tenant=_make_tenant(years=years),
        property=_make_property(mapped_property_id),
        room=_make_room(),
        financials=financials,
        guarantor=guarantor,
        period=Period(start_date=start_date, end_date=end_date),
        type_bail="Meublé",
        date_fin_theorique="31/12/2026",
        mention_speciale="",
    )


def _fetch_notion_payload_via_http(post_callable) -> dict:
    """Small helper used by tests to emulate HTTP calls to Notion endpoints."""
    endpoints = {
        "locataire": "https://api.notion.com/v1/databases/locataire-db/query",
        "bien": "https://api.notion.com/v1/databases/bien-db/query",
        "garants": "https://api.notion.com/v1/databases/garants-db/query",
    }
    result = {}
    for key, url in endpoints.items():
        response = post_callable(url, headers={"Authorization": "Bearer token"}, json={})
        response.raise_for_status()
        result[key] = response.json()
    return result


class TestGenerateLeaseUseCaseE2E:
    def test_generate_lease_renders_bail_and_caution_for_physical_guarantor(self):
        notion_payload = {
            "locataire": {"results": [{"id": "tenant-1", "properties": {"{NOM_LOCATAIRE}": "Dupont Jean"}}]},
            "bien": {"results": [{"id": "bien-1"}]},
            "garants": {"results": [{"id": "garant-1"}]},
        }

        def post_side_effect(url, **kwargs):
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            if "locataire" in url:
                mock_response.json.return_value = notion_payload["locataire"]
            elif "bien" in url:
                mock_response.json.return_value = notion_payload["bien"]
            else:
                mock_response.json.return_value = notion_payload["garants"]
            return mock_response

        renderer = MagicMock()
        placeholder_service = MagicMock()
        placeholder_service.generate_placeholders.return_value = {
            "{{NOM_LOCATAIRE}}": "Dupont Jean",
            "{{MONTANT_LOYER}}": "450",
        }

        guarantor = PhysicalGuarantor(
            full_name_raw="Pierre Dupont",
            email="pierre.dupont@email.com",
            phone_number="0611223344",
            address_raw="Paris",
            date_naissance="10/05/1965",
            lieu_naissance="Marseille",
        )
        lease = _make_lease(guarantor, date(2026, 1, 15), None, ["2026"])

        mocked_post = MagicMock(side_effect=post_side_effect)
        fetched = _fetch_notion_payload_via_http(mocked_post)

        assert mocked_post.call_count == 3
        assert fetched["locataire"]["results"][0]["id"] == "tenant-1"

        use_case = GenerateLeaseUseCase(renderer, placeholder_service)
        use_case.execute(lease)

        assert renderer.render.call_count == 2
        first_call = renderer.render.call_args_list[0].kwargs
        second_call = renderer.render.call_args_list[1].kwargs

        assert first_call["template_id"] == ID_TEMPLATE_BAIL_MEUBLE
        assert second_call["template_id"] == CAUTION_ID
        assert first_call["output_name"].startswith("Bail_location_")
        assert second_call["output_name"].startswith("Acte_de_caution_solidaire_")

    def test_generate_lease_renders_only_bail_for_visale(self):
        renderer = MagicMock()
        placeholder_service = MagicMock()
        placeholder_service.generate_placeholders.return_value = {"{{NOM_LOCATAIRE}}": "Dupont Jean"}

        guarantor = VisaleGuarantor(
            numero_visale="VISALE-2026-123",
            numero_contrat_visale="VC-001",
            date_emission_visale="01/01/2026",
        )
        lease = _make_lease(guarantor, date(2026, 1, 15), None, ["2026"])

        use_case = GenerateLeaseUseCase(renderer, placeholder_service)
        use_case.execute(lease)

        assert renderer.render.call_count == 1
        assert renderer.render.call_args.kwargs["template_id"] == ID_TEMPLATE_BAIL_MEUBLE


class TestGenerateReceiptUseCaseE2E:
    def test_generate_receipts_first_full_last_and_cleanup_after_departure(self):
        renderer = MagicMock()
        drive_adapter = MagicMock()
        placeholder_service = MagicMock()

        drive_adapter.get_or_create_subfolder.side_effect = ["year-folder", "recettes-folder", "at-folder"]
        placeholder_service.generate_placeholders.return_value = {"{{NOM_LOCATAIRE}}": "Dupont Jean"}

        lease = _make_lease(
            guarantor=PhysicalGuarantor(
                full_name_raw="Pierre Dupont",
                email="pierre.dupont@email.com",
                phone_number="0611223344",
                address_raw="Paris",
                date_naissance="10/05/1965",
                lieu_naissance="Marseille",
            ),
            start_date=date(2026, 1, 15),
            end_date=date(2026, 3, 10),
            years=["2026", "invalid-year"],
        )

        class FixedDateTime:
            @staticmethod
            def now():
                class D:
                    day = 7

                return D()

        with patch("src.use_cases.generate_receipt_use_case.datetime", FixedDateTime):
            use_case = GenerateReceiptUseCase(renderer, drive_adapter, placeholder_service)
            use_case.execute(lease)

        # Jan (first month), Feb (full month), Mar (last month)
        assert renderer.render.call_count == 3

        jan_call = renderer.render.call_args_list[0].kwargs
        feb_call = renderer.render.call_args_list[1].kwargs
        mar_call = renderer.render.call_args_list[2].kwargs

        assert jan_call["template_id"] == TEMPLATE_QUITTANCE_ID
        assert jan_call["folder_id"] == "at-folder"
        assert jan_call["placeholders"]["{{TITRE_DETAIL}}"] != ""
        assert "du 15 Janvier 2026 au 31 Janvier 2026" in jan_call["placeholders"]["{{PERIODE}}"]

        assert feb_call["placeholders"]["{{TITRE_DETAIL}}"] == ""
        assert feb_call["placeholders"]["{{PARAGRAPHE_DETAIL}}"] == ""

        assert mar_call["placeholders"]["{{TITRE_DETAIL}}"] != ""
        assert "du 01 Mars 2026 au 10 Mars 2026" in mar_call["placeholders"]["{{PERIODE}}"]

        # Apr -> Dec are after departure => cleanup of old receipts should be triggered.
        assert drive_adapter.delete_files_matching_regex.call_count == 9

        # Invalid year should be ignored and not create extra folders.
        assert drive_adapter.get_or_create_subfolder.call_count == 3

    def test_generate_receipts_skips_when_property_is_not_mapped(self):
        renderer = MagicMock()
        drive_adapter = MagicMock()
        placeholder_service = MagicMock()

        lease = _make_lease(
            guarantor=PhysicalGuarantor(
                full_name_raw="Pierre Dupont",
                email="pierre.dupont@email.com",
                phone_number="0611223344",
                address_raw="Paris",
                date_naissance="10/05/1965",
                lieu_naissance="Marseille",
            ),
            start_date=date(2026, 1, 15),
            end_date=None,
            years=["2026"],
        )
        lease.property.id = "not-mapped-property-id"

        use_case = GenerateReceiptUseCase(renderer, drive_adapter, placeholder_service)
        use_case.execute(lease)

        renderer.render.assert_not_called()
        drive_adapter.get_or_create_subfolder.assert_not_called()

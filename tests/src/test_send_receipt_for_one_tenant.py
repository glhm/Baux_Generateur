from main import *
def test_lambda_handler():
    sample_event = {
        "version": "2.0",
        "routeKey": "POST /TriggerBaux",
        "rawPath": "/TriggerBaux",
        "rawQueryString": "",
        "headers": {
            "accept-encoding": "gzip, br, deflate",
            "content-length": "82",
            "content-type": "application/json",
            "host": "7ysrbbxg08.execute-api.eu-west-3.amazonaws.com",
            "user-agent": "Make/production",
            "x-forwarded-for": "52.50.32.186",
            "x-forwarded-port": "443",
            "x-forwarded-proto": "https"
        },
        "requestContext": {
            "accountId": "515966541334",
            "apiId": "7ysrbbxg08",
            "domainName": "7ysrbbxg08.execute-api.eu-west-3.amazonaws.com",
            "http": {
                "method": "POST",
                "path": "/TriggerBaux",
                "protocol": "HTTP/1.1",
                "sourceIp": "52.50.32.186",
                "userAgent": "Make/production"
            },
            "requestId": "fmdiRhklCGYEPrQ=",
            "stage": "$default",
            "time": "13/Oct/2024:18:21:27 +0000",
            "timeEpoch": 1728843687839
        },
        "body": "{\"DataBaseItemID\": \"2c98e18b-dcb4-487c-8f5b-bc46bad9a462\",\"EnvoyerQuittance\":true}",
        "isBase64Encoded": False
    }
    context = None  
    print("Testing lambda_handler with sample event:")
    lambda_handler(sample_event, context)

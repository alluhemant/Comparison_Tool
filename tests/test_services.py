from fastapi import FastAPI
from fastapi.responses import Response
import json
from fastapi import HTTPException
from deepdiff import DeepDiff  # Make sure to import DeepDiff

app = FastAPI()

SAMPLE_XML = """<?xml version="1.0"?>
<data>
    <item>test</item>
</data>"""

# Parse the JSON string into a Python dictionary when the module loads
SAMPLE_JSON = json.loads("""
{
    "id": "AP03531491",
    "key": "202412171635067820902113",
    "brand": "01",
    "brandName": "Anthropologie",
    "orderDate": 1734465820,
    "status": "Cancelled",
    "emailAddress": "prancourt@mailinator.com",
    "currencySymbol": "$",
    "currencyCode": "USD",
    "primaryPaymentMethod": "CREDIT_CARD",
    "customerId": "125859350",
    "webProfileId": "beeb5fdf-ac7e-4cc3-8a56-0b4aff8c6bd0",
    "languageCode": "en-US",
    "messageNo": "920",
    "furnitureCode": "N",
    "returnMessageDays": "15",
    "returnMessageCode": "R",
    "orderPaymentStatus": "Approved",
    "displayPaymentMethod": "VISA",
    "siteId": "2",
    "reportEmptyPackage": "N",
    "orderPurpose": "Sales Order",
    "guestOrder": "No",
    "channel": "Web",
    "payments": [
        {
            "type": "VISA",
            "amount": {
                "authorized": 0.0,
                "charged": 0.0,
                "refunded": 0.0,
                "authId": "pi_3Qf780E6uXZznm3H1YdMloIH",
                "authCode": "616653",
                "requestAuthAmount": "155.95"
            },
            "creditCard": {
                "expirationMonth": "10",
                "expirationYear": "2030",
                "lastFourDigits": "1111"
            },
            "address": {
                "name": {
                    "last": "Savage",
                    "first": "Randy"
                },
                "country": "US",
                "address1": "2500 Broadway",
                "city": "Camden",
                "postalCode": "08104",
                "region": "NJ"
            }
        }
    ],
    "changeShipAdressFlag": "false",
    "cancelCode": "N",
    "priceInfo": {
        "rawSubtotal": 148.0,
        "currencyCode": "USD",
        "tax": 0.0,
        "duty": 0.0,
        "vat": {
            "total": 0.0
        },
        "flatRateShipping": 0.0,
        "overWeightRateShipping": 0.0,
        "shipping": 0.0,
        "deposit": 0.0,
        "giftWrapAmount": 0.0,
        "discounts": {
            "totalDiscount": 0.0
        },
        "total": 148.0,
        "rawSubtotalBeforeDiscounts": 148.0,
        "merchAdjustments": 0.0,
        "shippingAdjustments": 0.0,
        "taxAdjustments": 0.0,
        "flatRateShipFeeAdjustments": 0.0,
        "giftWrapAdjustments": 0.0,
        "priceAdjTotalGiftWrap": 0.0,
        "totalAdj": 0.0,
        "merchafterAdj": 148.0,
        "shippingAfterAdj": 0.0,
        "taxAfterAdj": 0.0,
        "flatRateShipFeeAfterAdj": 0.0,
        "giftWrapAfterAdj": 0.0,
        "totalAfterAdj": 148.0,
        "totalReturnRestockFee": 0.0,
        "totalReturnRestockFeeTax": 0.0,
        "totalSmartLabelFee": 0.0,
        "totalreturnFee": 0.0,
        "exchangeTotal": 0.0,
        "totalRefundAmount": 148.0,
        "amountRefunded": 148.0,
        "pendingRefund": 0.0
    },
    "shipments": [
        {
            "address": {
                "type": "CUSTOMER",
                "name": {
                    "last": "Savage",
                    "first": "Randy"
                },
                "address1": "2500 Broadway",
                "city": "Camden",
                "region": "NJ",
                "country": "US",
                "postalCode": "08104",
                "dayPhone": "1122112321",
                "collectionPointDetails": null
            },
            "notShipped": [
                {
                    "serviceLevel": "STANDARD",
                    "isTruckDelivery": false,
                    "isMarketplace": true,
                    "statusNum": "9000",
                    "status": "Cancelled",
                    "nodes": [
                        {
                            "nodetype": "MSN",
                            "marketplaceSellerInformation": [
                                {
                                    "sellerName": "ChannelAdvisor",
                                    "sellerEmail": "partnersupport@channeladvisor.com",
                                    "sellerPhoneNumber": "9192799779",
                                    "sellerReturnPolicy": "test test test"
                                }
                            ],
                            "marketplaceShipmentInformation": {
                                "marketplaceOrderId": "AP03531491-224363248-A",
                                "marketplaceCustomerId": "202412171634597820902836",
                                "miraklUrl": "https://urbanoutfitters-prod.mirakl.net/inbox/operator/threads/all?limit=50&search=AP03531491-224363248-A"
                            },
                            "items": [
                                {
                                    "id": "1",
                                    "orderLineKey": "202412171635067820902114",
                                    "linePrice": 148.0,
                                    "lineTax": "0.00",
                                    "lineTaxAfterAdj": "0.00",
                                    "lineDiscount": 0.0,
                                    "skuId": "79901450",
                                    "giftWrapFlag": false,
                                    "giftWrapAmount": 0.0,
                                    "quantity": 1,
                                    "maxCcRtnQty": "0",
                                    "naicsCode": "79901450",
                                    "IPDesc": "SCHUMACHER BETTY WALLPAPE PINK/ROSE ALL",
                                    "shipQty": "0",
                                    "returnCreateQty": "0",
                                    "returnRefundQty": "0",
                                    "returnReceiptQty": "0",
                                    "maxFCReturnQty": "0",
                                    "catalogInfo": {
                                        "faceOutImage": "//images.urbndata.com/is/image/Anthropologie/79901435_066_m",
                                        "product": {
                                            "productId": "79901435",
                                            "displayName": "Schumacher Betty Wallpaper",
                                            "a15productid": "AN-79901435-000"
                                        },
                                        "pdpUrl": "http://staging2.anthropologie.com/shop/product/AN-79901435-000"
                                    },
                                    "colorName": "Celadon",
                                    "sizeName": "One Size",
                                    "linePriceNet": 148.0,
                                    "linePricePerUnit": 148.0,
                                    "shippingSurcharge": "0",
                                    "shippingSurchargePerUnit": "0",
                                    "lineDiscountPerUnit": 0.0,
                                    "linePriceNetPerUnit": 148.0,
                                    "merchOrderAdj": "0",
                                    "netPriceAfterMerchOrderAdj": "148.00",
                                    "merchOrderAdjustments": [
                                        {
                                            "merchOrderAdjustment": {
                                                "adjustmentAmt": 0.0
                                            }
                                        },
                                        {
                                            "merchOrderAdjustment": {
                                                "adjustmentAmt": 0.0
                                            }
                                        }
                                    ],
                                    "skuType": "REGULAR",
                                    "status": "Cancelled",
                                    "orderLineQuantity": "0",
                                    "orderLineCancelQuantity": "1",
                                    "cancelFlag": "false",
                                    "isHazardous": false,
                                    "merchandiseClass": "9900",
                                    "exchangeEligible": false,
                                    "return": {
                                        "code": "RETURN_CLAIM_CODE_2",
                                        "maxQuantity": 0,
                                        "eligible": false
                                    },
                                    "claim": {
                                        "code": "RETURN_CLAIM_CODE_2",
                                        "maxQuantity": 0,
                                        "eligible": false
                                    }
                                }
                            ],
                            "totals": {
                                "merchBeforeDiscount": 148.0,
                                "merchDiscount": 0.0,
                                "merchAfterDiscount": 148.0,
                                "tax": 0.0,
                                "shipFees": 0.0,
                                "other": 0.0
                            }
                        }
                    ]
                }
            ]
        }
    ],
    "returnIsGiftable": "N",
    "creditCardFlagCode": "Y",
    "stripeCustomerId": "cus_RPweY7ucxrybS2",
    "transType": "D"
}
""")

@app.get("/tibco-xml")
def get_tibco_xml():
    return Response(content=SAMPLE_XML, media_type="application/xml")


@app.get("/python-xml")
def get_python_xml():
    return Response(content=SAMPLE_XML.replace("test", "modified_again"),
                    media_type="application/xml")


@app.get("/python-json")
def get_modified_json():
    try:
        # Create a modified version by making a copy of the dictionary
        modified = SAMPLE_JSON.copy()
        modified["brandName"] = "URBN"  # Your single field change

        # Calculate the diff
        diff = DeepDiff(SAMPLE_JSON, modified, ignore_order=True)

        return {
            "original": SAMPLE_JSON,
            "modified": modified,
            "diff": diff  # This contains structured difference info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
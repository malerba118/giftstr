import xmltodict

__author__ = 'austin'
import json
import bottlenose
from gift_finder import confidential


class AmazonService:
    AWS_ACCESS_KEY_ID="AKIAJJH5AIEKAJNIHPVA"
    AWS_SECRET_ACCESS_KEY=confidential.AWS_SECRET_ACCESS_KEY
    AWS_ASSOCIATE_TAG="austinmalerba-20"

    amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG)


    @staticmethod
    def productLookup(ASIN):
        print(ASIN)
        response = AmazonService.amazon.ItemLookup(
            ItemId=ASIN,
            IdType="ASIN",
            ResponseGroup="ItemAttributes,OfferSummary,Images"
        )

        d = xmltodict.parse(response)

        d = d["ItemLookupResponse"]["Items"]["Item"]

        return json.loads(json.dumps(d))

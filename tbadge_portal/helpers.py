import unicodedata
from hashids import Hashids
import logging

logger = logging.getLogger(__name__)


def purge_unicode(unicode_string):
    return unicodedata.normalize('NFKD', unicode_string).encode('ascii', 'ignore')


def hashid(hash_val, conversion_type):
    if not isinstance(hash_val, int) and conversion_type == "encode":
        hash_val = int(hash_val)
    hashid_key = Hashids(salt='#REDACTED', min_length='#REDACTED')
    if conversion_type == "decode":
        try:
            return hashid_key.decode(hash_val)[0]
        except IndexError:
            logger.critical("status_code={} message={}".format(400, "Incorrect hashid value attempted to be decoded."))
            return None
    if conversion_type == "encode":
        return hashid_key.encode(hash_val)

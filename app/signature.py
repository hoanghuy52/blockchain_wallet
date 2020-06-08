from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC


class Signature:
    encoding = 'utf-8'
    dss_mode = 'fips-186-3'
    ecc_curve = 'secp256r1'
    key_format = 'DER'

    @staticmethod
    def generate():
        """
        Generate PEM Key-Pair
        :return: (private_key, public_key)
        """
        private_key = ECC.generate(curve=Signature.ecc_curve)
        public_key = private_key.public_key()
        der_prv = private_key.export_key(format=Signature.key_format)
        der_pub = public_key.export_key(format=Signature.key_format)
        return der_prv.hex(), der_pub.hex()

    @staticmethod
    def get_public_key(private_key):
        _private_key = ECC.import_key(bytes.fromhex(private_key))
        _public_key = _private_key.public_key()
        der_pub = _public_key.export_key(format=Signature.key_format)
        return der_pub.hex()

    @staticmethod
    def sign(private_key: str, data: str) -> str:
        """
        Sign messages
        :param private_key: Private Key PEM
        :param data: Data to send
        :return: Hex Signature
        """
        bytes_data = data.encode(Signature.encoding)
        hash_data = SHA256.new(bytes_data)

        prv_key = ECC.import_key(bytes.fromhex(private_key))

        signer = DSS.new(prv_key, Signature.dss_mode)
        signature = signer.sign(hash_data)

        return signature.hex()

    @staticmethod
    def verify(public_key: str, signature: str, data: str):
        """
        Verify Data With Public Key
        :param public_key: String
        :param signature: String
        :param data: String
        :return: ValueError – if the signature is not authentic
                try:
                    verifier.verify(h, signature)
                    print "The message is authentic."
                 except ValueError:
                   print "The message is not authentic."
        """
        _signature = bytes.fromhex(signature)
        _public_key = ECC.import_key(bytes.fromhex(public_key))

        bytes_data = data.encode(Signature.encoding)
        hash_data = SHA256.new(bytes_data)

        verify_key = DSS.new(_public_key, Signature.dss_mode)
        return verify_key.verify(hash_data, _signature)



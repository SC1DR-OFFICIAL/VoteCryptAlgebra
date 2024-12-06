# voting/crypto.py

import tenseal as ts

class HomomorphicEncryption:
    def __init__(self):
        # Создаём контекст шифрования с необходимыми параметрами
        self.context = ts.context(
            ts.SCHEME_TYPE.BFV,
            poly_modulus_degree=4096,
            plain_modulus=65537  # Обязательно укажите plain_modulus
        )
        self.context.global_scale = 2**40
        self.context.generate_galois_keys()

    def encrypt_vote(self, value):
        if not isinstance(value, int):
            raise ValueError("Value must be an integer.")
        # Создаём вектор из одного элемента и шифруем его
        return ts.bfv_vector(self.context, [value])

    def decrypt_vote(self, serialized_vote):
        if not isinstance(serialized_vote, bytes):
            raise TypeError("serialized_vote must be bytes.")
        # Десериализуем объект BFVVector
        encrypted_vote = ts.bfv_vector_from(self.context, serialized_vote)
        # Дешифруем и возвращаем значение
        decrypted_value = encrypted_vote.decrypt()[0]
        return decrypted_value

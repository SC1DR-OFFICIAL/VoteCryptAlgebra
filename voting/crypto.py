# voting/crypto.py

import os
from pathlib import Path
import tenseal as ts

# Путь к директории для хранения ключей
BASE_DIR = Path(__file__).resolve().parent.parent
KEYS_DIR = BASE_DIR / 'keys'

# Убедитесь, что директория для ключей существует
os.makedirs(KEYS_DIR, exist_ok=True)

# Файл для хранения сериализованного контекста
CONTEXT_FILE = KEYS_DIR / 'context.bin'

class HomomorphicEncryption:
    def __init__(self):
        if not CONTEXT_FILE.exists():
            self.generate_keys()
        else:
            self.load_keys()

    def generate_keys(self):
        print("Generating new HE context and keys...")
        # Настройка контекста для BFV схемы с параметром 'plain_modulus'
        context = ts.context(
            ts.SCHEME_TYPE.BFV,
            poly_modulus_degree=8192,
            plain_modulus=1032193,  # Обязательный параметр для BFV схемы
            coeff_mod_bit_sizes=[60, 40, 40, 60],
            n_threads=1
        )
        context.generate_galois_keys()
        context.generate_relin_keys()

        # Сериализация и сохранение всего контекста в один файл
        with open(CONTEXT_FILE, 'wb') as f:
            f.write(context.serialize())

        self.context = context
        print("HE context and keys generated and saved.")

    def load_keys(self):
        print("Loading existing HE context and keys...")
        # Загрузка сериализованного контекста из файла
        with open(CONTEXT_FILE, 'rb') as f:
            context_bytes = f.read()
        context = ts.context_from(context_bytes)

        self.context = context
        print("HE context and keys loaded.")

    def encrypt_vote(self, candidate_id):
        """Функция для шифрования идентификатора кандидата."""
        # Преобразование целого числа в зашифрованный объект
        encrypted_vote = ts.bfv_vector(context=self.context, data=[int(candidate_id)])
        return encrypted_vote.serialize()

    def decrypt_vote(self, encrypted_vote_bytes):
        """Функция для расшифровки зашифрованного голоса."""
        # Десериализация зашифрованного объекта
        encrypted_vote = ts.deserialize(encrypted_vote_bytes, self.context)
        decrypted_vote = encrypted_vote.decrypt()
        return decrypted_vote[0]

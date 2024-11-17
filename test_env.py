from decouple import AutoConfig

config = AutoConfig(search_path='.')
print(config("SECRET_KEY"))

import yaml

with open("recipes/saison_sally.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

print(cfg)

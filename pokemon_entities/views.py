import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404

from .models import PokemonEntity, Pokemon

MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = "https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832&fill=transparent"


def add_pokemon(folium_map, lat, lon, name, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        tooltip=name,
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemons = Pokemon.objects.all()
    pokemons_entities = PokemonEntity.objects.all()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemons_entities:
        if pokemon_entity.pokemon.picture:
            add_pokemon(
                folium_map, pokemon_entity.lat, pokemon_entity.lon,
                pokemon_entity.pokemon.title, pokemon_entity.pokemon.picture.path)
        else:
            add_pokemon(
                folium_map, pokemon_entity.lat, pokemon_entity.lon,
                pokemon_entity.pokemon.title)

    pokemons_on_page = []
    for pokemon in pokemons:
        if pokemon.picture:
            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'img_url': pokemon.picture.url,
                'title_ru': pokemon.title,
            })
        else:
            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'title_ru': pokemon.title,
            })

    return render(request, "mainpage.html", context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)

    for pokemon_entity in pokemon.pokemon_entities.all():
        if pokemon.picture:
            add_pokemon(
                folium_map, pokemon_entity.lat, pokemon_entity.lon,
                pokemon.title, pokemon.picture.path)
        else:
            add_pokemon(
                folium_map, pokemon_entity.lat, pokemon_entity.lon,
                pokemon.title)

    pokemon_data = {
        'title_ru': pokemon.title,
        'description': pokemon.description,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
    }

    if pokemon.picture:
        pokemon_data['img_url'] = pokemon.picture.url


    if pokemon.previous_evolution:
        pokemon_data['previous_evolution'] = {
            'title_ru': pokemon.previous_evolution.title,
            'pokemon_id': pokemon.previous_evolution.id,
        }
        if pokemon.previous_evolution.picture:
            pokemon_data['previous_evolution']['img_url'] = pokemon.previous_evolution.picture.url

    try:
        next_evolution = pokemon.next_evolutions.first()
        if next_evolution:
            pokemon_data['next_evolution'] = {
                'title_ru': next_evolution.title,
                'pokemon_id': next_evolution.id,
            }
            if next_evolution.picture:
                pokemon_data['next_evolution']['img_url'] = next_evolution.picture.url
    except (IndexError, ObjectDoesNotExist):
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')


    return render(request, "pokemon.html", context={'map': folium_map._repr_html_(),
                                                    'pokemon': pokemon_data})

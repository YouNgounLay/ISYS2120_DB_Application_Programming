"use strict";

class App
{
    constructor()
    {
    }

    build_query(text, limit=20, offset=0)
    {
        /* ';' sperated string, item with = for metadata match */

        var parsed = {
            'term': [],
            'metadata': {},
            'invaild': [],
            'limit': limit,
            'offset': offset, // not implemented yet
        };

        text.split(';').forEach(
            item => {
                var segs = item.trim().split("=");
                switch (segs.length) {
                case 1:
                    parsed.term.push(...segs[0].trim().split(" "));
                    break;
                case 2:
                    var key = segs[0].trim();
                    var value = segs[1].trim();
                    if (key in parsed.metadata) {
                        parsed.metadata[key].push(value);
                    } else {
                        parsed.metadata[key] = [value];
                    }
                    break;
                default:
                    parsed.invaild.push(item);
                }
            }
        );
        return parsed;
    }

    __add_movie_item(m)
    {
        $('#movie-search-list-body').append(
            $("<tr />").attr({'class': "clickable-tr"}).on('click', () => {
                window.location.href='/movie/' + m.movie_id;
            }).append(
                $("<td />").attr({"style": "text-align: center;"}).text(m.movie_id),
                $("<td />").text(m.movie_title),
                $("<td />").text(m.release_year),
            )
        );
    }

    __rebuild_movie_search_list(items)
    {
        $('#movie-search-list-body').empty();
        items.forEach(item => {
            this.__add_movie_item(item);
        });
    }

    movie_get_hint()
    {
        this.__movie_get_hint($("#movie-search-box").val());
    }

    movie_fuzzy_search()
    {
        this.__movie_fuzzy_search($("#movie-search-box").val());
    }

    __movie_get_hint(search_text)
    {
        $.ajax({
            method: "POST",
            url: "/api/gethint",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                type: 'movie',
                query: this.build_query(search_text)
            })
        }).done((json) => {
            if (json.code != 0){
                console.log(json)
            }
            this.__rebuild_movie_search_list(json.payload);
        });
    }

    __movie_fuzzy_search(search_text)
    {
        $.ajax({
            method: "POST",
            url: "/api/search",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                type: 'movie',
                query: this.build_query(search_text, 50)
            })
        }).done((json) => {
            if (json.code != 0){
                console.log(json);
            }
            this.__rebuild_movie_search_list(json.payload);
        });
    }
}
var app = new App();

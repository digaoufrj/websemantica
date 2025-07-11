
def get_film_by_title_query(title):
    
    return f"""
    SELECT DISTINCT ?film ?filmName ?director ?directorName 
       (GROUP_CONCAT(DISTINCT CONCAT("(", ?actorName, ", ", REPLACE(STR(?actor), ".*entity/", ""), ")"); separator=" | ") AS ?actorTuples)
       ?year 
       (COALESCE(?logo, ?image) AS ?displayImage)
       (GROUP_CONCAT(DISTINCT ?genreLabel; separator=", ") AS ?genres)
WHERE {{
  ?film rdfs:label "{title}"@en.
  ?film rdfs:label ?filmName.
  FILTER (lang(?filmName) = "en")

  ?film wdt:P31 wd:Q11424.
  ?film wdt:P57 ?director.
  ?film wdt:P577 ?date.
  ?film wdt:P161 ?actor.

  OPTIONAL {{ ?film wdt:P18 ?image. }}     
  OPTIONAL {{ ?film wdt:P154 ?logo. }}    
  OPTIONAL {{ ?film wdt:P136 ?genre. }}    

  ?director rdfs:label ?directorName.
  FILTER (lang(?directorName) = "en")

  ?actor rdfs:label ?actorName.
  FILTER (lang(?actorName) = "en")

  OPTIONAL {{
    ?genre rdfs:label ?genreLabel.
    FILTER (lang(?genreLabel) = "en")
  }}

  BIND(YEAR(?date) AS ?year)
}}
GROUP BY ?film ?filmName ?director ?directorName ?year ?image ?logo

    """


def get_films_by_actor_query(actor_id):
   
    return f"""
    SELECT DISTINCT ?film ?filmName ?director ?directorName 
       (GROUP_CONCAT(DISTINCT CONCAT("(", ?actorName, ", ", REPLACE(STR(?actor), ".*entity/", ""), ")"); separator=" | ") AS ?actorTuples)
       ?year 
       (COALESCE(?logo, ?image) AS ?displayImage)
       (GROUP_CONCAT(DISTINCT ?genreLabel; separator=", ") AS ?genres)
WHERE {{
  ?film wdt:P31 wd:Q11424.
  ?film wdt:P161 wd:{actor_id}.               
  ?film wdt:P57 ?director.
  ?film wdt:P577 ?date.
  ?film wdt:P161 ?actor.

  OPTIONAL {{ ?film wdt:P18 ?image. }}     
  OPTIONAL {{ ?film wdt:P154 ?logo. }}     
  OPTIONAL {{ ?film wdt:P136 ?genre. }}    

  ?film rdfs:label ?filmName.
  FILTER (lang(?filmName) = "en")

  ?director rdfs:label ?directorName.
  FILTER (lang(?directorName) = "en")

  ?actor rdfs:label ?actorName.
  FILTER (lang(?actorName) = "en")

  OPTIONAL {{
    ?genre rdfs:label ?genreLabel.
    FILTER (lang(?genreLabel) = "en")
  }}

  BIND(YEAR(?date) AS ?year)
}}
GROUP BY ?film ?filmName ?director ?directorName ?year ?image ?logo
LIMIT 100
    """



def get_films_by_director_query(director_id):
   
    return f"""
    SELECT DISTINCT ?film ?filmName ?director ?directorName 
       (GROUP_CONCAT(DISTINCT CONCAT("(", ?actorName, ", ", REPLACE(STR(?actor), ".*entity/", ""), ")"); separator=" | ") AS ?actorTuples)
       ?year 
       (COALESCE(?logo, ?image) AS ?displayImage)
       (GROUP_CONCAT(DISTINCT ?genreLabel; separator=", ") AS ?genres)
WHERE {{
  ?film wdt:P31 wd:Q11424.
  ?film wdt:P57 wd:{director_id}.               
  ?film wdt:P57 ?director.
  ?film wdt:P577 ?date.
  ?film wdt:P161 ?actor.

  OPTIONAL {{ ?film wdt:P18 ?image. }}    
  OPTIONAL {{ ?film wdt:P154 ?logo. }}    
  OPTIONAL {{ ?film wdt:P136 ?genre. }}    

  ?film rdfs:label ?filmName.
  FILTER (lang(?filmName) = "en")

  ?director rdfs:label ?directorName.
  FILTER (lang(?directorName) = "en")

  ?actor rdfs:label ?actorName.
  FILTER (lang(?actorName) = "en")

  OPTIONAL {{
    ?genre rdfs:label ?genreLabel.
    FILTER (lang(?genreLabel) = "en")
  }}

  BIND(YEAR(?date) AS ?year)
}}
GROUP BY ?film ?filmName ?director ?directorName ?year ?image ?logo
    """


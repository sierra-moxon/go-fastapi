import requests


# Respect the method name for run_sparql_on with enums
def run_solr_on(solr_instance, category, id, fields):
    """
    Return the result of a solr query on the given solrInstance (Enum ESOLR), for a certain document_category (ESOLRDoc) and id
    """
    query = (
        solr_instance.value
        + 'select?q=*:*&fq=document_category:"'
        + category.value
        + '"&fq=id:"'
        + id
        + '"&fl='
        + fields
        + "&wt=json&indent=on"
    )
    response = requests.get(query)
    return response.json()["response"]["docs"][0]


def run_solr_text_on(solr_instance, category, q, qf, fields, optionals):
    """
    Return the result of a solr query on the given solrInstance (Enum ESOLR), for a certain document_category (ESOLRDoc) and id
    """
    if optionals is None:
        optionals = ""
    query = (
        solr_instance.value
        + "select?q="
        + q
        + "&qf="
        + qf
        + '&fq=document_category:"'
        + category.value
        + '"&fl='
        + fields
        + "&wt=json&indent=on"
        + optionals
    )
    logger.info("QUERY: ", query)

    response = requests.get(query)
    return response.json()["response"]["docs"]

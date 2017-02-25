MonthlyRating
-------------

* `GET /api/ratings/monthly/`

Returns:
{
    "success": true,
    "data": [{
        "id": <int>,
        "year": <int>,
        "month": <int>,
        "is_approved": <bool>
    }]
}


* `GET /api/ratings/monthly/{id}/`

Returns:
{
    "success": true,
    "data": {
        "id": <int>,
        "year": <int>,
        "month": <int>,
        "base_document": {
            "id": <int>,
            "description": <str>,
            "description_imp": <str>
        },
        "is_negotiated": <bool>,
        "is_approved": <bool>,
        "approved_by": {
            "id": <int>,
            "first_name": <str>,
            "last_name": <str>,
            "patronymic": <str>
        },  # OPTIONAL
        "components": [{
            "id": <int>,
            "rating_component": {
                "id": <int>,
                "number": <int>,
                "base_document": {
                    "id": <int>,
                    "description": <str>,
                    "description_imp": <str>
                },
                "name": <str>,
                "base_description": <str>,
                "weight": <int>
            },
            "responsible": {
                "id": <int>,
                "first_name": <str>,
                "last_name": <str>,
                "patronymic": <str>
            },  # OPTIONAL
            "additional_description": <str>,  # OPTIONAL
            "negotiator_comment": <str>,  # OPTIONAL
            "region_comment": <str>,  # OPTIONAL
            "values": [{
                "region_id": <int>,
                "value": <decimal>  # max_digits=8, decimal_places=2, if
            }],
        }]
    }
}

* `GET /api/ratings/monthly/last_approved`

Same as previous, but returns last approved

* `GET /api/ratings/monthly/current`

Same as previous, but returns current


MonthlyRatingComponent
----------------------

* `GET /api/ratings/monthly/components/{id}/`

Returns:
{
    "success": true,
    "data": {
        "id": <int>,
        "rating_component": {
            "id": <int>,
            "number": <int>,
            "base_document": {
                "id": <int>,
                "description": <str>,
                "description_imp": <str>
            },
            "name": <str>,
            "base_description": <str>,
            "weight": <int>,
            "sub_components_display_type": <int>  # 1 - decimal, 2 - percent
        },
        "sub_components": [{
            "id": <int>
            "name": <str>,  # max 1000 symbols
            "date": <str>,  # OPTIONAL YYYY-MM-DD
            "responsible": {
                "id": <int>,
                "first_name": <str>,
                "last_name": <str>,
                "patronymic": <str>
            },  # OPTIONAL prefecture_employee
            "values": [{
                "region_id": <int>,
                "is_average": <bool>,
                "value": <decimal>  # max_digits=8, decimal_places=2, absent if
                                    # is_average == true
            }],
            "best_type": <int>,  # 1 - "min", 2 - "max"
            "description": <str>,  # unlimited
            "document_link": <str>  # URL to file download
        }]
    }
}


* `PATCH /api/ratings/monthly/components/{id}/negotiator_comment`

Body: {
    "negotiator_comment": <str>
}

Returns:
{
    "success": true
}


* `PATCH /api/ratings/monthly/components/{id}/region_comment`

Body: {
    "region_comment": <str>
}

Returns:
{
    "success": true
}


MonthlyRatingSubComponent
-------------------------

* `POST /api/ratings/monthly/sub_components/`

Body:
{
    "component_id": <int>,
    "name": <str>,  # max 1000 symbols
    "date": <str>,  # OPTIONAL YYYY-MM-DD
    "responsible": <int>,  # OPTIONAL prefecture_employee id
    "values": [{
        "region": <int>,  # region id
        "is_average": <bool>,
        "value": <decimal>  # max_digits=8, decimal_places=2, if
                            # is_average == true, should not be presented
    }],
    "best_type": <str>,  # "min"|"max"
    "description": <str>,  # unlimited
    "document": <str>  # base64
}

Returns:
{
    "success": true
    "data": {
        "sub_component_id": <int>
    }
}


* `PUT /api/ratings/monthly/sub_components/{id}/`

Body:
{
    "id": <int>,
    "name": <str>,  # max 1000 symbols
    "date": <str>,  # OPTIONAL YYYY-MM-DD
    "responsible": <int>,  # OPTIONAL prefecture_employee id
    "values": [{
        "region_id": <int>,
        "is_average": <bool>,
        "value": <decimal>  # max_digits=8, decimal_places=2, if
                            # is_average == true, should not be presented
    }],
    "best_type": <str>,  # "min"|"max"
    "description": <str>,  # unlimited
    "document": <str>  # OPTIONAL, base64, if not presented, old "document_link" will not be changed
}

Returns:
{
    "success": true
}


* `DELETE /api/ratings/monthly/sub_components/{id}/`

Returns:
{
    "success": true
}
Regions
_______

* `GET /api/map/regions/`

.. code-block:: javascript

    [{
        "id": <int>,
        "name": <str>,
        "district": <int>
    }]

PrefectureEmployees
___________________

* `GET /api/employees/prefecture_employees/`  # OPTIONAL `?include_approvers=true`

.. code-block:: javascript

    [{
        "id": <int>,
        "first_name": <str>,
        "last_name": <str>,
        "patronymic": <str>
    }]

MonthlyRating
-------------

* `GET /api/ratings/monthly/`

.. code-block:: javascript

    [{
        "id": <int>,
        "year": <int>,
        "month": <int>,
        "is_negotiated": <bool>,
        "is_approved": <bool>
    }]

* `GET /api/ratings/monthly/{id}/`

.. code-block:: javascript

    {
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
        } | null, // OPTIONAL
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
                "weight": <int>,
                "sub_components_display_type": <int>  // 1 - decimal, 2 - percent
            },
            "responsible": {
                "id": <int>,
                "first_name": <str>,
                "last_name": <str>,
                "patronymic": <str>
            } | null,  // OPTIONAL
            "additional_description": <str> | null,  // OPTIONAL
            "negotiator_comment": <str> | null,  // OPTIONAL
            "region_comment": <str> | null,  // OPTIONAL
            "values": [{
                "region_id": <int>,
                "value": <decimal> | null  // OPTIONAL max_digits=8, decimal_places=2
            }],
        }]
    }

* `GET /api/ratings/monthly/last_approved/`

Same as previous, but returns last approved

* `GET /api/ratings/monthly/current/`

Same as previous, but returns current


MonthlyRatingComponent
----------------------

* `GET /api/ratings/monthly/components/{id}/` `?include_related=true`

.. code-block:: javascript

    {
        "id": <int>,
        "monthly_rating": {
            "id": <int>,
            "year": <int>,
            "month": <int>,
            "is_approved": <bool>
        },
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
            "sub_components_display_type": <int>  // 1 - decimal, 2 - percent
        },
        "responsible": {
            "id": <int>,
            "first_name": <str>,
            "last_name": <str>,
            "patronymic": <str>
        } | null,  // OPTIONAL
        // if include_related == 'true'
        "related_sub_components": [{
            "id": <int>
            "name": <str>,  // max 1000 symbols
            "date": <str>,  // OPTIONAL YYYY-MM-DD
            "responsible": {
                "id": <int>,
                "first_name": <str>,
                "last_name": <str>,
                "patronymic": <str>
            },  // OPTIONAL prefecture_employee
            "values": [{
                "region": <int>,  // region_id
                "is_average": <bool>,
                "value": <decimal>  // max_digits=8, decimal_places=2, absent if
                                    // is_average == true
            }],
            "best_type": <int>,  // 1 - "min", 2 - "max"
            "description": <str>,  // unlimited
            "document": <str>  // URL to file download
        }]
    }

* `PATCH /api/ratings/monthly/components/{id}/negotiator_comment/`

.. code-block:: javascript

    {
        "negotiator_comment": <str>
    }

Returns:

.. code-block:: javascript

    {}

* `PATCH /api/ratings/monthly/components/{id}/region_comment/`

.. code-block:: javascript

    {
        "region_comment": <str>
    }

Returns:

.. code-block:: javascript

    {}

MonthlyRatingSubComponent
-------------------------

* `GET /api/ratings/monthly/sub_components/{id}/`

.. code-block:: javascript

    {
        "id": <int>
        "name": <str>,  // max 1000 symbols
        "date": <str>,  // OPTIONAL YYYY-MM-DD
        "responsible": {
            "id": <int>,
            "first_name": <str>,
            "last_name": <str>,
            "patronymic": <str>
        },  // OPTIONAL prefecture_employee
        "values": [{
            "region": <int>,  // region_id
            "is_average": <bool>,
            "value": <decimal>  // max_digits=8, decimal_places=2, absent if
                                // is_average == true
        }],
        "best_type": <int>,  // 1 - "min", 2 - "max"
        "description": <str>,  // unlimited
        "document": <str>  // URL to file download
    }

* `POST /api/ratings/monthly/sub_components/?component_id=<int>`

.. code-block:: javascript

    {
        "name": <str>,  // max 1000 symbols
        "date": <str>,  // OPTIONAL YYYY-MM-DD
        "responsible": <int>,  // OPTIONAL prefecture_employee id
        "values": [{
            "region": <int>,  // region id
            "is_average": <bool>,
            "value": <decimal> | null // max_digits=8, decimal_places=2, if
                                      // is_average == true, should be null
        }],
        "best_type": <int>,  // 1 - "min", 2 - "max"
        "description": <str>,  // unlimited
        "document": <str> | null  // base64
    }

Returns:

.. code-block:: javascript

    {
        GET body
    }

* `PUT /api/ratings/monthly/sub_components/{id}/`

If user is responsible for whole component:

.. code-block:: javascript

    {
        "name": <str>,  // max 1000 symbols
        "date": <str>,  // OPTIONAL YYYY-MM-DD
        "responsible": <int>,  // OPTIONAL prefecture_employee id
        "values": [{
            "region_id": <int>,
            "is_average": <bool>,
            "value": <decimal> | null  // max_digits=8, decimal_places=2, if
                                       // is_average == true, should be null
        }],
        "best_type": <int>,  // 1 - "min", 2 - "max"
        "description": <str>,  // unlimited
        "document": <str>  // base64
    }

If user is responsible for sub_component only:

.. code-block:: javascript

    {
        "name": <str>,  // max 1000 symbols
        "date": <str>,  // OPTIONAL YYYY-MM-DD
        "values": [{
            "region_id": <int>,
            "is_average": <bool>,
            "value": <decimal> | null  // max_digits=8, decimal_places=2, if
                                       // is_average == true, should be null
        }],
        "best_type": <int>,  // 1 - "min", 2 - "max"
        "description": <str>,  // unlimited
        "document": <str>  // base64
    }

Returns:  # 200

.. code-block:: javascript

    {
        GET body
    }

* `DELETE /api/ratings/monthly/sub_components/{id}/`

Returns:  # 204

=============
Authorization
=============

* `POST /api/auth/login`

.. code-block:: javascript

    {
        "email": <str>,
        "password": <str>
    }

Returns: # 200 OK

* `POST /api/auth/logout`

.. code-block:: javascript

    {}

Returns: # 200 OK

* `POST /api/auth/reset_password`

.. code-block:: javascript

    {}

Returns: # 200 OK

=======
Regions
=======

* `GET /api/map/regions/`

.. code-block:: javascript

    [{
        "id": <int>,
        "name": <str>,
        "district": <int>
    }]

===================
PrefectureEmployees
===================

* `GET /api/employees/prefecture_employees/`  # OPTIONAL `?include_approvers=true`

.. code-block:: javascript

    [{
        "id": <int>,
        "first_name": <str>,
        "last_name": <str>,
        "patronymic": <str>
    }]

=============
MonthlyRating
=============

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
        "elements": [{
            "id": <int>,
            "rating_element": {
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
                "value": <decimal> | null  // OPTIONAL max_digits=8, decimal_places=5
            }],
        }]
    }

* `GET /api/ratings/monthly/current/`

.. code-block:: javascript

    {
        "id": <int>,  // rating id to load
    }

====================
MonthlyRatingElement
====================

* `GET /api/ratings/monthly/elements/{id}/`  # OPTIONAL `?include_related=true`

.. code-block:: javascript

    {
        "id": <int>,
        "monthly_rating": {
            "id": <int>,
            "year": <int>,
            "month": <int>,
            "is_approved": <bool>
        },
        "rating_element": {
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
        },
        "responsible": {
            "id": <int>,
            "first_name": <str>,
            "last_name": <str>,
            "patronymic": <str>
        } | null,  // OPTIONAL
        // if include_related == 'true'
        "values": {
            <region_id>: <decimal>
        }
        "related_sub_elements": [{
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
                "value": <decimal>  // max_digits=8, decimal_places=5, absent if
                                    // is_average == true
            }],
            "best_type": <int>,  // 1 - "min", 2 - "max"
            "display_type": <int>, // 1 - number, 2 - percent
            "description": <str>,  // unlimited
            "document": <str>  // URL to file download
        }]
    }

* `PATCH /api/ratings/monthly/elements/{id}/`

.. code-block:: javascript

    {
        "responsible": <int>  // responsible_id
    }

.. code-block:: javascript

    {
        "additional_description": <str>
    }

.. code-block:: javascript

    {
        "negotiator_comment": <str>
    }

.. code-block:: javascript

    {
        "region_comment": <str>
    }

Returns:

.. code-block:: javascript

    {}

=======================
MonthlyRatingSubElement
=======================

* `GET /api/ratings/monthly/sub_elements/{id}/`

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
            "value": <decimal>  // max_digits=8, decimal_places=5, absent if
                                // is_average == true
        }],
        "best_type": <int>,  // 1 - "min", 2 - "max"
        "description": <str>,  // unlimited
        "document": <str>  // URL to file download
    }

* `POST /api/ratings/monthly/sub_elements/?element_id=<int>`

.. code-block:: javascript

    {
        "id": <int>,
        "name": <str>,  // max 1000 symbols
        "date": <str>,  // OPTIONAL YYYY-MM-DD
        "responsible": <int>,  // OPTIONAL prefecture_employee id
        "values": [{
            "region": <int>,  // region id
            "is_average": <bool>,
            "value": <decimal> | null // max_digits=8, decimal_places=5, if
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

* `PATCH /api/ratings/monthly/sub_elements/{id}/`

If user is responsible for whole element:

.. code-block:: javascript

    {
        "name": <str>,  // max 1000 symbols
        "date": <str>,  // OPTIONAL YYYY-MM-DD
        "responsible": <int>,  // OPTIONAL prefecture_employee id
        "values": [{
            "id": <int>,
            "region_id": <int>,
            "is_average": <bool>,
            "value": <decimal> | null  // max_digits=8, decimal_places=5, if
                                       // is_average == true, should be null
        }],
        "best_type": <int>,  // 1 - "min", 2 - "max"
        "description": <str>,  // unlimited
        "document": <str>  // base64
    }

If user is responsible for sub_element only:

.. code-block:: javascript

    {
        "name": <str>,  // max 1000 symbols
        "date": <str>,  // OPTIONAL YYYY-MM-DD
        "values": [{
            "id": <int>,
            "region_id": <int>,
            "is_average": <bool>,
            "value": <decimal> | null  // max_digits=8, decimal_places=5, if
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

* `DELETE /api/ratings/monthly/sub_elements/{id}/`

Returns:  # 204

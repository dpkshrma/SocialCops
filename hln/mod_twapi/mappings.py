doc_mappings = {
    "lead": {
        "properties": {
            "categories": {
                "type": "string"
            },
            "calc_categories": {
                "type": "string"
            },
            "created_at": {
                "type": "date",
                "format": "yyyy/MM/dd HH:mm:ss"
            },
            "data": {
                "type": "nested",
                "properties": {
                    "entities": {
                        "type": "nested",
                        "properties": {
                            "id": {
                                "type": "long"
                            },
                            "name": {
                                "type": "string"
                            },
                            "screen_name": {
                                "type": "string"
                            }
                        }
                    },
                    "media": {
                        "type": "nested",
                        "properties": {
                            "id": {
                                "type": "long"
                            },
                            "media_url": {
                                "type": "string"
                            },
                            "type": {
                                "type": "string"
                            }
                        }
                    },
                    "text": {
                        "type": "string"
                    }
                }
            },
            "id": {
                "type": "long"
            },
            "coordinates": {
                "type": "geo_point"
            },
            "reporter_id": {
                "type": "long"
            }
        }
    },
    "reporter": {
        "properties": {
            "id": {
                "type": "long"
            },
            "name": {
                "type": "string"
            },
            "screen_name":{
                "type": "string"
            },
            "profile_image_url":{
                "type": "string"
            },
            "profile_background_image_url":{
                "type": "string"
            },
            "created_at":{
                "type": "date",
                "format": "yyyy/MM/dd HH:mm:ss"
            },
            "location":{
                "type": "string"
            }
        }
    }
}
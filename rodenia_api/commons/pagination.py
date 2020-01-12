"""Simple helper to paginate query
"""
from flask import url_for, request
from rodenia_api.commons import util
import json


def schema_dump(schema, page_obj):
    # doing this because postgres result returns Decimal() object and
    # schema.dump can't serialize that.
    dump = schema.dumps(page_obj.items, cls=util.DecimalEncoder).data
    return json.loads(dump)


def paginate(query, schema, initial_page_size=10, initial_page_number=1):
    page = int(request.args.get('page', initial_page_number))
    page_size = int(request.args.get('page_size', initial_page_size))
    page_obj = query.paginate(page=page, per_page=page_size)

    next = url_for(
        request.endpoint,
        page=page_obj.next_num if page_obj.has_next else page_obj.page,
        page_size=page_size,
        **request.view_args
    )
    
    prev = url_for(
        request.endpoint,
        page=page_obj.prev_num if page_obj.has_prev else page_obj.page,
        page_size=page_size,
        **request.view_args
    )
    

    return {
        'total': page_obj.total,
        'pages': page_obj.pages,
        'next': next,
        'prev': prev,
        'results': schema_dump(schema, page_obj)
    }

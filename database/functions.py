def _parse_params(params=None, joinTerm=' and ', quote=True, notIncludedCols=None):
    if not notIncludedCols: notIncludedCols = []
    if not params: return ''
    paramsList = ['{}="{}"'.format(k, v) if quote else '{}={}'.format(k, v)
                  for k, v in params.items() if k not in notIncludedCols]
    return joinTerm.join(paramsList)

def _paginateDict(data, link, params=None, limit=10, offset=0):
    currParams, nextParams, prevParams = params.copy(),params.copy(),params.copy()
    currParamsStr, nextParamsStr, prevParamsStr = '', '', ''

    currParams['limit']=limit
    currParams['offset']=offset
    currParamsStr = link+ '?' + _parse_params(currParams, '&', quote=False)

    nextOffset = offset + limit
    nextPaginate = len(data['data']) > 0
    if nextPaginate:
        nextParams['limit'] = limit
        nextParams['offset'] = nextOffset
        nextParamsStr = link+ '?' + _parse_params(nextParams, '&', quote=False)

    prevOffset = -1
    if offset - limit > 0: prevOffset = offset-limit
    elif offset > 0: prevOffset = 0
    prevPaginate = prevOffset>-1
    if prevPaginate:
        prevParams['limit'] = limit
        prevParams['offset'] = prevOffset
        prevParamsStr = link+ '?' + _parse_params(prevParams, '&', quote=False)
    data['paginate'] = {
        'currPage': currParamsStr,
        'prevPage': prevParamsStr,
        'nextPage': nextParamsStr
    }
    return data

def _make_id_link(data, url, key):
    for d in data:
        d['link'] = url.format(d[key])
    return data

def get_from_db(cnx, table='', q=None, params=None, fields='*', paginate=False, limit=10, offset=0,
                url='', custUrl='', notIncludedCols=None, urlNotIncludedCols=None):
    cursor = cnx.cursor()
    query = """Select {} from CatalogService.{}""".format(fields, table)
    if q: query = q
    paramsStr = _parse_params(params, ' and ', notIncludedCols=notIncludedCols)
    if paramsStr: query += """\nwhere {}""".format(paramsStr)
    if paginate: query += """\nlimit {}, {}""".format(offset, limit)
    cursor.execute(query)
    data = {'data': cursor.fetchall()}
    cnx.commit()
    cursor.close()
    # print(query)
    if custUrl: url = custUrl
    else: url = url + table
    if paginate:
        custParams = params.copy()
        if urlNotIncludedCols:
            for c in urlNotIncludedCols:
                if c in custParams: del custParams[c]
        data = _paginateDict(data, url, params=custParams, limit=limit, offset=offset)
    print(query)
    return data

def get_last_id(cnx):
    cursor = cnx.cursor()
    queryID = """SELECT LAST_INSERT_ID() as lastID;"""
    cursor.execute(queryID)
    data = cursor.fetchall()
    if data: return str(data[0]['lastID'])
    else: raise Exception('')

def add_db(cnx, table, params):
    if type(params)!=list:
        params = [params]
    paramsCheck = None
    for p in params:
        if not paramsCheck: paramsCheck = set(list(p.keys()))
        else:
            for k in p.keys():
                if k not in paramsCheck: raise Exception('Different add parameters found in params list')
    colNames = params[0].keys()
    cols = ', '.join(colNames)
    vals = []
    for p in params:
        vals.append('(' + ', '.join(['"' + p[c] + '"' for c in colNames]) + ')')
    vals = ', '.join(vals)
    query = """INSERT into CatalogService.{} ({}) values {};""".format(table, cols, vals)
    return get_from_db(cnx, q=query)

def delete_db(cnx, table, params):
    paramsStr = _parse_params(params, ' and ')
    query = """DELETE FROM CatalogService.{} WHERE {};""".format(table,paramsStr)
    return get_from_db(cnx, q=query)

def update_db(cnx, table, checkParams, addParams):
    checkParamsStr = _parse_params(checkParams, ' and ')
    addParamsStr = _parse_params(addParams, ', ')
    query = """UPDATE CatalogService.{} SET {} WHERE {};""".format(table, addParamsStr, checkParamsStr)
    return get_from_db(cnx, q=query)

def convert_datetime_str(data, cols=None):
    if not cols: cols = ['meetingDate', 'bookingDate']
    for i,d in enumerate(data):
        for c in cols:
            if c in d: data[i][c] = str(d[c])
    return data

def convert_str_datetime(data, cols=None):
    pass
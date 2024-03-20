from pysnmp.hlapi.v3arch.asyncio import *


async def get(snmpEngine, communityName, address, port, id):
    get_result = await getCmd(
        snmpEngine,
        CommunityData(communityName, mpModel=0),
        UdpTransportTarget((address, port)),
        ObjectType(id),
    )

    return await get_result

async def next(snmpEngine, communityName, address, port, id):
    next_result = await nextCmd(
        snmpEngine,
        CommunityData(communityName, mpModel=0),
        UdpTransportTarget((address, port)),
        ObjectType(id),
    )

    return await next_result

async def bulk(snmpEngine, communityName, address, port, nonRepeaters, maxRepetitions, id):
    bulk_result = await bulkCmd(
        snmpEngine,
        CommunityData(communityName, mpModel=0),
        UdpTransportTarget((address, port)),
        nonRepeaters,
        maxRepetitions,
        ObjectType(id),
    )

    return await bulk_result

async def set(snmpEngine, communityName, address, port, id, data):
    set_result = await setCmd(
        snmpEngine,
        CommunityData(communityName, mpModel=0),
        UdpTransportTarget((address, port)),
        ObjectType(id, data),
    )

    return await set_result


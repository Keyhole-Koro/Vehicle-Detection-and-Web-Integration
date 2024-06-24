require('dotenv').config();
const { RingApi } = require('ring-client-api');
const fs = require('fs');
const path = require('path');

async function scanCamera() {
    const ringApi = new RingApi({
        refreshToken: process.env.RING_REFRESH_TOKEN
    });

    const locations = await ringApi.getLocations();
    const cameras = locations.flatMap(location => location.cameras);
    
    if (cameras.length === 0) {
        console.log('No cameras found');
        return;
    }

    console.log(cameras);
}

scanCamera();

require('dotenv').config();
const { RingApi } = require('ring-client-api');
const fs = require('fs');
const path = require('path');

async function getSnapshot() {
    const ringApi = new RingApi({
        refreshToken: process.env.RING_REFRESH_TOKEN
    });

    const locations = await ringApi.getLocations();
    const cameras = locations.flatMap(location => location.cameras);
    
    if (cameras.length === 0) {
        console.log('No cameras found');
        return;
    }

    const camera = cameras[0];
    console.log(`Getting snapshot from ${camera.name}...`);

    try {
        const snapshotBuffer = await camera.getSnapshot();
        const filePath = path.join(__dirname, './result/snapshot.jpg');
        fs.writeFileSync(filePath, snapshotBuffer);
        console.log(`Snapshot saved to ${filePath}`);
    } catch (error) {
        console.error('Failed to get snapshot:', error);
    }
}

getSnapshot();

/**
 * api.onRefreshTokenUpdated
 * https://github.com/dgreif/ring/wiki/Refresh-Tokens
 */
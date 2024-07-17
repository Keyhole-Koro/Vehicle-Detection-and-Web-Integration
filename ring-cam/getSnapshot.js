require('dotenv').config();
const { RingApi } = require('ring-client-api');
const fs = require('fs');
const path = require('path');

let refreshToken = process.env.RING_REFRESH_TOKEN;

async function getAccessToken(refreshToken) {
    try {
        const ringApi = new RingApi({ refreshToken });
        const accessToken = await ringApi.getAccessToken();
        return accessToken;
    } catch (error) {
        console.error('Error refreshing token:', error.message);
        throw error;
    }
}

async function getSnapshot() {
    try {
        const ringApi = new RingApi({
            refreshToken
        });

        const locations = await ringApi.getLocations();
        const cameras = locations.flatMap(location => location.cameras);

        const cameraIds = process.env.TARGET_CAMERA_IDS.split(',');

        const stickupCameras = cameras.filter(camera => cameraIds.includes(`${camera.initialData.id}`));

        const camera = stickupCameras[0];
        console.log(`Getting snapshot from ${camera.initialData.description}...`);

        const snapshotBuffer = await camera.getSnapshot();
        const filePath = path.join(__dirname, './result/snapshot.jpg');
        fs.writeFileSync(filePath, snapshotBuffer);
        console.log(`Snapshot saved to ${filePath}`);
    } catch (error) {
        console.error('Failed to get snapshot:', error);
    }
}

getSnapshot();

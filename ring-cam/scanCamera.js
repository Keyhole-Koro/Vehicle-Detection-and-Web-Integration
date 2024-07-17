require('dotenv').config();
const { RingApi } = require('ring-client-api');

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

async function scanCameras() {
    try {
        const ringApi = new RingApi({
            refreshToken
        });

        const locations = await ringApi.getLocations();
        const cameras = locations.flatMap(location => location.cameras);

        const cameraIds = process.env.TARGET_CAMERA_IDS.split(',');

        const stickupCameras = cameras.filter(camera => cameraIds.includes(`${camera.initialData.id}`));

        // Output camera details
        stickupCameras.forEach(camera => {
            console.log(`ID: ${camera.initialData.id}`);
            console.log(`Description: ${camera.initialData.description}`);
            console.log(`Latitude: ${camera.initialData.latitude}, Longitude: ${camera.initialData.longitude}`);
            console.log(`Battery Life: ${camera.initialData.battery_life}`);
            console.log(`Firmware Version: ${camera.initialData.firmware_version}`);
            console.log('-----------------------------');
        });

    } catch (error) {
        console.error('Error fetching cameras:', error);
    }
}

scanCameras();

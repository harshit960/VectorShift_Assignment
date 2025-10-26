import { useState, useEffect } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
} from '@mui/material';
import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { HubSpotIntegration } from './integrations/hubspot';
import { DataForm } from './data-form';

const integrationMapping = {
    'Notion': NotionIntegration,
    'Airtable': AirtableIntegration,
    'HubSpot': HubSpotIntegration,
};

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState(null);
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);
    const CurrIntegration = integrationMapping[currType];
    useEffect(() => {
        if (!integrationParams) return;
        localStorage.setItem('auth', JSON.stringify(integrationParams));
    }, [integrationParams])
    useEffect(() => {
        const auth = localStorage.getItem('auth');
        if (auth) {
            if(JSON.parse(auth).credentials.expiry_timestamp && Date.now() < JSON.parse(auth).credentials.expiry_timestamp) {
                console.log('Session expired, please re-authenticate.');
                localStorage.removeItem('auth');
                setIntegrationParams(null);
                setCurrType(null);
                return;
            }
            setIntegrationParams(JSON.parse(auth));
            console.log(JSON.parse(auth).type);
            setCurrType(JSON.parse(auth).type);
        }
    }, []);
    return (
        <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' sx={{ width: '100%' }}>
            <Box display='flex' flexDirection='column'>
                {/* <TextField
            label="User"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            sx={{mt: 2}}
        />
        <TextField
            label="Organization"
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            sx={{mt: 2}}
        /> */}
                <Autocomplete
                    id="integration-type"
                    options={Object.keys(integrationMapping)}
                    value={integrationParams?.type || currType}
                    sx={{ width: 300, mt: 2 }}
                    renderInput={(params) => <TextField {...params} label="Integration Type" />}
                    onChange={(e, value) => {
                        setCurrType(value); setIntegrationParams(null);
                    }}
                />
            </Box>
            {currType &&
                <Box className='flex space-x-4 items-end justify-center'>
                    <CurrIntegration className='flex items-center justify-center' user={user} org={org} integrationParams={integrationParams} setIntegrationParams={setIntegrationParams} />
                    {integrationParams?.credentials &&
                        <button
                            onClick={() => {
                                localStorage.removeItem('auth');
                                setIntegrationParams(null);
                                setCurrType(null);
                            }}
                            className='bg-red-500 text-white p-2 rounded hover:bg-red-600 transition duration-200'
                        >
                            Logout
                        </button>
                    }
                </Box>
            }
            {integrationParams?.credentials &&
                <Box sx={{ mt: 2 }}>
                    <DataForm integrationType={integrationParams?.type} credentials={integrationParams?.credentials} />
                </Box>
            }
        </Box>
    );
}

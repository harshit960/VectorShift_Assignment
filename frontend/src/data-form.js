import { useState } from 'react';
import {
    Box,
    TextField,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Typography,
} from '@mui/material';
import axios from 'axios';

const endpointMapping = {
    'Notion': 'notion',
    'Airtable': 'airtable',
    'HubSpot': 'hubspot',
};

export const DataForm = ({ integrationType, credentials }) => {
    const [loadedData, setLoadedData] = useState(null);
    const endpoint = endpointMapping[integrationType];

    const handleLoad = async () => {
        try {
            const formData = new FormData();
            formData.append('credentials', JSON.stringify(credentials));
            const response = await axios.post(`http://localhost:8000/integrations/${endpoint}/load`, formData);
            const data = response.data;
            setLoadedData(data);
        } catch (e) {
            alert(e?.response?.data?.detail);
        }
    }

    const renderDataTable = () => {
        if (!loadedData || !Array.isArray(loadedData) || loadedData.length === 0) {
            return (
                <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
                    No data loaded
                </Typography>
            );
        }

        return (
            <TableContainer component={Paper} sx={{ mt: 2, maxHeight: 400 }}>
                <Table stickyHeader>
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Name</TableCell>
                            <TableCell>Creation Time</TableCell>
                            <TableCell>Last Modified</TableCell>
                            <TableCell>Visibility</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {loadedData.map((item, index) => (
                            <TableRow key={item.id || index}>
                                <TableCell>{item.id}</TableCell>
                                <TableCell>{item.type}</TableCell>
                                <TableCell>{item.name}</TableCell>
                                <TableCell>
                                    {item.creation_time ? new Date(item.creation_time).toLocaleString() : 'N/A'}
                                </TableCell>
                                <TableCell>
                                    {item.last_modified_time ? new Date(item.last_modified_time).toLocaleString() : 'N/A'}
                                </TableCell>
                                <TableCell>{item.visibility ? 'Yes' : 'No'}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        );
    };

    return (
        <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' width='100%'>
            <Box display='flex' flexDirection='column' width='100%'>
                {renderDataTable()}
                <Button
                    onClick={handleLoad}
                    sx={{mt: 2}}
                    variant='contained'
                >
                    Load Data
                </Button>
                <Button
                    onClick={() => setLoadedData(null)}
                    sx={{mt: 1}}
                    variant='contained'
                >
                    Clear Data
                </Button>
            </Box>
        </Box>
    );
}

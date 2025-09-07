# VectorShift Integrations Technical Assessment

This project is a technical assessment for VectorShift that demonstrates building OAuth integrations with third-party services. The application consists of a React frontend and FastAPI backend that handle OAuth flows for multiple integration platforms.

## 🏗️ Project Structure

```
VectorShift_Assignment/
├── backend/
│   ├── main.py                     # FastAPI application entry point
│   ├── redis_client.py             # Redis client configuration
│   ├── requirements.txt            # Python dependencies
│   └── integrations/
│       ├── integration_item.py     # IntegrationItem data model
│       ├── airtable.py            # Airtable OAuth integration
│       ├── notion.py              # Notion OAuth integration
│       └── hubspot.py             # HubSpot OAuth integration (implemented)
└── frontend/
    ├── package.json               # Node.js dependencies
    ├── src/
    │   ├── App.js                 # Main React component
    │   ├── integration-form.js    # Integration selection UI
    │   ├── data-form.js          # Data display component
    │   └── integrations/
    │       ├── airtable.js       # Airtable frontend integration
    │       ├── notion.js         # Notion frontend integration
    │       ├── slack.js          # Slack frontend integration
    │       └── hubspot.js        # HubSpot frontend integration (implemented)
```

## 🎯 Assessment Objectives

### Part 1: HubSpot OAuth Integration
- Complete the `hubspot.py` backend integration with OAuth2 flow
- Implement frontend HubSpot integration in `hubspot.js`
- Add HubSpot integration to the UI

### Part 2: Loading HubSpot Items
- Implement `get_items_hubspot` function to retrieve data from HubSpot
- Return structured `IntegrationItem` objects
- Display integration items (console output recommended)

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- Redis server

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start Redis server:
```bash
redis-server
```

4. Start the FastAPI backend:
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Programming language
- **Redis** - In-memory data structure store for session management
- **httpx/requests** - HTTP clients for API integrations
- **uvicorn** - ASGI server implementation

### Frontend
- **React 18** - JavaScript library for building user interfaces
- **Material-UI** - React component library
- **Axios** - HTTP client for API requests
- **Tailwind CSS** - Utility-first CSS framework

## 🔐 OAuth Integration Setup

### Setting Up Test Credentials

For testing purposes, you'll need to create OAuth applications for each service:

#### HubSpot
1. Go to [HubSpot Developer Portal](https://developers.hubspot.com/)
2. Create a new app
3. Configure OAuth settings with redirect URI: `http://localhost:8000/integrations/hubspot/oauth2callback`
4. Note your Client ID and Client Secret

#### Notion (Optional)
1. Go to [Notion Developer Portal](https://developers.notion.com/)
2. Create a new integration
3. Configure OAuth settings
4. Note your Client ID and Client Secret

#### Airtable (Optional)
1. Go to [Airtable Developer Portal](https://airtable.com/developers/apps)
2. Create a new app
3. Configure OAuth settings
4. Note your Client ID and Client Secret

### Environment Configuration

Create a `.env` file in the backend directory with your credentials:

```env
# HubSpot
HUBSPOT_CLIENT_ID=your_hubspot_client_id
HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret

# Notion (Optional)
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret

# Airtable (Optional)
AIRTABLE_CLIENT_ID=your_airtable_client_id
AIRTABLE_CLIENT_SECRET=your_airtable_client_secret
```

## 📋 Implementation Guidelines

### Backend Integration Structure
Each integration should implement:
- `authorize_{service}()` - Initiate OAuth flow
- `oauth2callback_{service}()` - Handle OAuth callback
- `get_{service}_credentials()` - Retrieve stored credentials
- `get_items_{service}()` - Fetch and return IntegrationItem objects

### Frontend Integration Structure
Each integration should implement:
- Authorization initiation
- Credential retrieval
- Data fetching and display
- Error handling

### IntegrationItem Schema
The `IntegrationItem` class includes fields such as:
- `id` - Unique identifier
- `name` - Display name
- `type` - Item type
- `url` - Resource URL
- Additional service-specific fields

## 🧪 Testing

1. Start all services (Redis, backend, frontend)
2. Navigate to `http://localhost:3000`
3. Select HubSpot integration
4. Complete OAuth flow
5. Verify data retrieval and display


## 🔗 Useful Resources

- [HubSpot API Documentation](https://developers.hubspot.com/docs/api/overview)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)


# Disaster Response Dashboard - Maharashtra

A comprehensive emergency management system for disaster response operations in Maharashtra, featuring real-time SOS tracking, resource management, and interactive mapping.

## 🚀 Features

### Core Functionality
- **Real-time SOS Management**: Track emergency requests with priority-based ticketing
- **Interactive Map View**: Visualize all SOS requests, shelters, and hospitals on an interactive map
- **Resource Management**: Monitor shelter capacity and hospital bed availability
- **Regional Analytics**: Break down data by Western, Central, and Vidarbha regions
- **User Authentication**: Role-based access control (Admin, Responder, Viewer)

### Dashboard Components
- **Overview Statistics**: Real-time counts and metrics
- **Critical Alerts**: High-priority SOS requests and resource shortages
- **Recent Activity**: Latest updates and status changes
- **Charts & Analytics**: Regional breakdowns and trend analysis

### Technical Features
- **Geospatial Support**: PostgreSQL + PostGIS for location-based queries
- **Real-time Updates**: WebSocket support for live data
- **Responsive Design**: Modern UI built with React and Tailwind CSS
- **API Integration**: RESTful API for external integrations (n8n workflows)

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   n8n Workflow  │───▶│  FastAPI Backend│───▶│ PostgreSQL +    │
│   (Data Source) │    │   (REST API)    │    │   PostGIS DB    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  React Frontend │
                       │   (Dashboard)   │
                       └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL + PostGIS**: Geospatial database
- **SQLAlchemy**: ORM for database operations
- **GeoAlchemy2**: PostGIS integration
- **JWT**: Authentication and authorization

### Frontend
- **React 18**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **Mapbox GL**: Interactive mapping
- **Recharts**: Data visualization
- **Lucide React**: Icon library

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ with PostGIS extension
- Mapbox API key (for mapping features)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd disaster-response-dashboard
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env
# Edit .env with your configuration

# Set up database
# Create PostgreSQL database with PostGIS extension
createdb disaster_response
psql disaster_response -c "CREATE EXTENSION postgis;"

# Run the application
python main.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
# Create .env.local with:
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAPBOX_TOKEN=your_mapbox_token

# Start development server
npm start
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

> **Note:**  
> If you see an error like `ERR_ADDRESS_INVALID` when trying to access `http://0.0.0.0:8001/`, use `http://localhost:8001/` or `http://127.0.0.1:8001/` instead.  
> `0.0.0.0` is a special address that means "all network interfaces" and is not directly accessible from your browser.  
> Always use `localhost`, `127.0.0.1`, or your server's actual IP/domain in your browser's address bar.

## 📊 Data Structure

### SOS Request Format (from n8n)
```json
{
  "id": 1755968763493,
  "status": "Done",
  "people": 1,
  "lon": "77.301",
  "lat": "30.139",
  "text": "Still no electricity since yesterday. Water supply is erratic. Please send any available relief kits for our area. We are running out of essentials.",
  "place": "Surat, Gujarat",
  "timestamp": "",
  "category": "Needs Rescue"
}
```

### API Endpoints

#### SOS Management
- `POST /api/sos/` - Create new SOS request
- `GET /api/sos/` - List SOS requests with filters
- `GET /api/sos/map` - Get SOS data for map visualization
- `PUT /api/sos/{id}` - Update SOS request status
- `GET /api/sos/stats/summary` - Get SOS statistics

#### Resources
- `GET /api/shelters/` - List shelters with capacity info
- `GET /api/hospitals/` - List hospitals with bed availability
- `GET /api/shelters/nearby` - Find nearby shelters
- `GET /api/hospitals/nearby` - Find nearby hospitals

#### Dashboard
- `GET /api/dashboard/stats` - Overall statistics
- `GET /api/dashboard/regions` - Regional breakdown
- `GET /api/dashboard/critical-alerts` - High-priority alerts

## 🔐 Authentication

### Default Users
- **Admin**: `admin` / `admin123`
- **Responder**: `responder` / `responder123`
- **Viewer**: `viewer` / `viewer123`

### User Roles
- **Admin**: Full access to all features
- **Responder**: Can update ticket status and resource information
- **Viewer**: Read-only access to dashboard and maps

## 🗺️ Map Configuration

The system uses Mapbox for interactive mapping. To enable map features:

1. Get a Mapbox access token from [mapbox.com](https://mapbox.com)
2. Set `REACT_APP_MAPBOX_TOKEN` in your frontend environment
3. Maps will automatically display SOS requests, shelters, and hospitals

## 📱 Features by Page

### Dashboard
- Overview statistics and metrics
- Real-time charts and analytics
- Critical alerts and notifications
- Recent activity feed

### Tickets
- List view of all SOS requests
- Advanced filtering and search
- Status updates and assignment
- Priority-based sorting

### Map View
- Interactive map with all resources
- Layer controls for different resource types
- Real-time marker updates
- Location-based filtering

### Resources
- Shelter capacity management
- Hospital bed availability
- Resource center inventory
- Regional resource distribution

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/disaster_response
SECRET_KEY=your-secret-key
DEBUG=True
```

#### Frontend (.env.local)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAPBOX_TOKEN=your-mapbox-token
```

### Database Configuration
- Enable PostGIS extension for geospatial features
- Configure connection pooling for production
- Set up regular backups

## 🚀 Deployment

### Production Considerations
- Use environment variables for sensitive data
- Set up proper CORS configuration
- Enable HTTPS
- Configure database connection pooling
- Set up monitoring and logging
- Use production-grade database (PostgreSQL 13+)

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
3. Add tests if applicable
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

## 🔮 Future Enhancements

- **Mobile App**: Native mobile applications for responders
- **AI Integration**: Predictive analytics for resource allocation
- **IoT Integration**: Real-time sensor data from disaster areas
- **Multi-language Support**: Localization for different regions
- **Advanced Analytics**: Machine learning for disaster prediction
- **Integration APIs**: Connect with government systems and NGOs

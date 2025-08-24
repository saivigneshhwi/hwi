import React, { useState, useEffect } from 'react';
import { 
  Users, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  MapPin,
  Activity
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [regionStats, setRegionStats] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [criticalAlerts, setCriticalAlerts] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, regionRes, activityRes, alertsRes] = await Promise.all([
        axios.get('/api/dashboard/stats'),
        axios.get('/api/dashboard/regions'),
        axios.get('/api/dashboard/recent-activity'),
        axios.get('/api/dashboard/critical-alerts')
      ]);

      setStats(statsRes.data);
      setRegionStats(regionRes.data);
      setRecentActivity(activityRes.data);
      setCriticalAlerts(alertsRes.data);
    } catch (error) {
      toast.error('Failed to fetch dashboard data');
      console.error('Dashboard data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      1: 'bg-gray-100 text-gray-700',
      2: 'bg-blue-100 text-blue-700',
      3: 'bg-yellow-100 text-yellow-700',
      4: 'bg-orange-100 text-orange-700',
      5: 'bg-red-100 text-red-700'
    };
    return colors[priority] || colors[1];
  };

  const getStatusColor = (status) => {
    const colors = {
      'Pending': 'bg-yellow-100 text-yellow-800',
      'In Progress': 'bg-blue-100 text-blue-800',
      'Done': 'bg-green-100 text-green-800',
      'Cancelled': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors['Pending'];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="spinner"></div>
      </div>
    );
  }

  const chartData = regionStats.map(region => ({
    name: region.region,
    'SOS Requests': region.sos_count,
    'People Affected': region.people_affected
  }));

  const pieData = [
    { name: 'Pending', value: stats?.pending_sos || 0, color: '#f59e0b' },
    { name: 'In Progress', value: stats?.in_progress_sos || 0, color: '#3b82f6' },
    { name: 'Completed', value: stats?.completed_sos || 0, color: '#22c55e' }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Overview of disaster response operations</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Activity className="w-4 h-4" />
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total SOS Requests</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_sos || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">People Affected</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_people_affected || 0}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Shelter Capacity</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.available_shelter_capacity || 0}</p>
              <p className="text-sm text-gray-500">Available</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Hospital Beds</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.available_hospital_beds || 0}</p>
              <p className="text-sm text-gray-500">Available</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Region Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">SOS Requests by Region</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="SOS Requests" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status Pie Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Request Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Critical Alerts */}
      {criticalAlerts && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <span>Critical Alerts</span>
            </h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Critical SOS */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">High Priority SOS ({criticalAlerts.critical_sos.length})</h4>
                <div className="space-y-2">
                  {criticalAlerts.critical_sos.slice(0, 3).map((sos) => (
                    <div key={sos.id} className="p-3 bg-red-50 rounded-lg border border-red-200">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-red-800">{sos.category}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(sos.priority)}`}>
                          P{sos.priority}
                        </span>
                      </div>
                      <p className="text-sm text-red-700 mt-1">{sos.place}</p>
                      <p className="text-xs text-red-600 mt-1">{sos.people} people affected</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Full Shelters */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Shelters at Capacity ({criticalAlerts.full_shelters.length})</h4>
                <div className="space-y-2">
                  {criticalAlerts.full_shelters.slice(0, 3).map((shelter) => (
                    <div key={shelter.id} className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                      <p className="text-sm font-medium text-orange-800">{shelter.name}</p>
                      <p className="text-sm text-orange-700 mt-1">{shelter.address}</p>
                      <p className="text-xs text-orange-600 mt-1">
                        {shelter.occupancy}/{shelter.capacity} occupied
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Low Bed Hospitals */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Low Bed Availability ({criticalAlerts.low_bed_hospitals.length})</h4>
                <div className="space-y-2">
                  {criticalAlerts.low_bed_hospitals.slice(0, 3).map((hospital) => (
                    <div key={hospital.id} className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                      <p className="text-sm font-medium text-yellow-800">{hospital.name}</p>
                      <p className="text-sm text-yellow-700 mt-1">{hospital.address}</p>
                      <p className="text-xs text-yellow-600 mt-1">
                        {hospital.available_beds}/{hospital.total_beds} beds available
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <Clock className="w-5 h-5 text-gray-500" />
            <span>Recent Activity</span>
          </h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <Activity className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {activity.category} - {activity.place}
                  </p>
                  <p className="text-sm text-gray-600">
                    {activity.people} people affected • Priority {activity.priority}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                    {activity.status}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

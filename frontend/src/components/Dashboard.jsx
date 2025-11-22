import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  Upload, 
  Receipt, 
  Calculator, 
  Users, 
  LogOut,
  Plus,
  Eye
} from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [taxReturns, setTaxReturns] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [docsRes, receiptsRes, returnsRes] = await Promise.all([
        axios.get('/api/documents'),
        axios.get('/api/receipts'),
        axios.get('/api/returns')
      ]);

      setDocuments(docsRes.data);
      setReceipts(receiptsRes.data);
      setTaxReturns(returnsRes.data);

      // If user is CPA, fetch clients
      if (user.user_type === 'cpa') {
        const clientsRes = await axios.get('/api/cpa/clients');
        setClients(clientsRes.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event, type) => {
    const file = event.target.files[0];
    if (!file) return;

    // Show loading state
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    
    if (type === 'document') {
      formData.append('document_type', 'other');
    } else if (type === 'receipt') {
      formData.append('category', 'business');
      formData.append('amount', '0');
      formData.append('date', new Date().toISOString().split('T')[0]);
    }

    try {
      const response = await axios.post(`/api/${type === 'document' ? 'documents' : 'receipts'}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      console.log('Upload successful:', response.data);
      await fetchData(); // Refresh data
      
      // Clear the file input
      event.target.value = '';
      
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const createTaxReturn = async () => {
    try {
      await axios.post('/api/returns', { year: new Date().getFullYear() });
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Error creating tax return:', error);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      draft: 'secondary',
      in_review: 'default',
      filed: 'success'
    };
    return <Badge variant={variants[status] || 'secondary'}>{status}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4 text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Sore Financial Group Tax Portal</h1>
            <p className="text-muted-foreground">
              Welcome back, {user.profile?.firstName || user.email}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline">{user.user_type}</Badge>
            <Button variant="outline" onClick={logout}>
              <LogOut className="mr-2 h-4 w-4" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="receipts">Receipts</TabsTrigger>
            <TabsTrigger value="returns">Tax Returns</TabsTrigger>
            {user.user_type === 'cpa' && <TabsTrigger value="clients">Clients</TabsTrigger>}
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Documents</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{documents.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Tax documents uploaded
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Receipts</CardTitle>
                  <Receipt className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{receipts.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Expense receipts
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Tax Returns</CardTitle>
                  <Calculator className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{taxReturns.length}</div>
                  <p className="text-xs text-muted-foreground">
                    Returns in progress
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common tasks to get you started</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Hidden file input for quick upload */}
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e, 'document')}
                  className="hidden"
                  id="quick-document-upload"
                />
                <Button className="h-20 flex-col gap-2" asChild>
                  <label htmlFor="quick-document-upload" className="cursor-pointer">
                    <Upload className="h-6 w-6" />
                    Upload Documents
                  </label>
                </Button>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileUpload(e, 'receipt')}
                  className="hidden"
                  id="quick-receipt-upload"
                />
                <Button variant="outline" className="h-20 flex-col gap-2" asChild>
                  <label htmlFor="quick-receipt-upload" className="cursor-pointer">
                    <Receipt className="h-6 w-6" />
                    Add Receipt
                  </label>
                </Button>
                <Button variant="outline" className="h-20 flex-col gap-2" onClick={createTaxReturn}>
                  <Plus className="h-6 w-6" />
                  New Tax Return
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Tax Documents</CardTitle>
                <CardDescription>Manage your uploaded tax documents</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => handleFileUpload(e, 'document')}
                      className="hidden"
                      id="document-upload"
                    />
                    <Button asChild>
                      <label htmlFor="document-upload" className="cursor-pointer">
                        <Upload className="mr-2 h-4 w-4" />
                        Upload Document
                      </label>
                    </Button>
                  </div>
                  
                  {documents.length === 0 ? (
                    <p className="text-muted-foreground">No documents uploaded yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {documents.map((doc) => (
                        <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <p className="font-medium">{doc.document_type}</p>
                            <p className="text-sm text-muted-foreground">
                              Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                            </p>
                          </div>
                          <Button variant="outline" size="sm">
                            <Eye className="mr-2 h-4 w-4" />
                            View
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Receipts Tab */}
          <TabsContent value="receipts" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Expense Receipts</CardTitle>
                <CardDescription>Track your business expenses</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={(e) => handleFileUpload(e, 'receipt')}
                      className="hidden"
                      id="receipt-upload"
                    />
                    <Button asChild>
                      <label htmlFor="receipt-upload" className="cursor-pointer">
                        <Upload className="mr-2 h-4 w-4" />
                        Upload Receipt
                      </label>
                    </Button>
                  </div>
                  
                  {receipts.length === 0 ? (
                    <p className="text-muted-foreground">No receipts uploaded yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {receipts.map((receipt) => (
                        <div key={receipt.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <p className="font-medium">${receipt.amount}</p>
                            <p className="text-sm text-muted-foreground">
                              {receipt.category} • {new Date(receipt.date).toLocaleDateString()}
                            </p>
                          </div>
                          <Button variant="outline" size="sm">
                            <Eye className="mr-2 h-4 w-4" />
                            View
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tax Returns Tab */}
          <TabsContent value="returns" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Tax Returns</CardTitle>
                <CardDescription>Manage your tax return filings</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Button onClick={createTaxReturn}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create New Tax Return
                  </Button>
                  
                  {taxReturns.length === 0 ? (
                    <p className="text-muted-foreground">No tax returns created yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {taxReturns.map((taxReturn) => (
                        <div key={taxReturn.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <p className="font-medium">Tax Year {taxReturn.year}</p>
                            <p className="text-sm text-muted-foreground">
                              Created {new Date(taxReturn.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {getStatusBadge(taxReturn.status)}
                            <Button variant="outline" size="sm">
                              <Eye className="mr-2 h-4 w-4" />
                              View
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Clients Tab (CPA only) */}
          {user.user_type === 'cpa' && (
            <TabsContent value="clients" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Client Management</CardTitle>
                  <CardDescription>Manage your client accounts</CardDescription>
                </CardHeader>
                <CardContent>
                  {clients.length === 0 ? (
                    <p className="text-muted-foreground">No clients found.</p>
                  ) : (
                    <div className="space-y-2">
                      {clients.map((client) => (
                        <div key={client.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <p className="font-medium">
                              {client.profile?.firstName} {client.profile?.lastName}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {client.email} • {client.user_type}
                            </p>
                          </div>
                          <Button variant="outline" size="sm">
                            <Users className="mr-2 h-4 w-4" />
                            Manage
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          )}
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;

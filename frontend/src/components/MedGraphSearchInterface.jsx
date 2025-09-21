import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Brain, 
  Shield, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Target,
  Zap,
  Eye,
  BookOpen,
  Activity
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'

const MedGraphSearchInterface = ({ systemInitialized, apiConnected, apiBaseUrl }) => {
  const [query, setQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState(null)
  const [searchHistory, setSearchHistory] = useState([])
  const [searchMode, setSearchMode] = useState('enhanced')
  
  // Advanced search options
  const [useVerification, setUseVerification] = useState(true)
  const [topK, setTopK] = useState(10)
  const [societyFilter, setSocietyFilter] = useState('')
  const [yearFilter, setYearFilter] = useState('')
  
  // Clinical search options
  const [patientContext, setPatientContext] = useState('')
  const [evidenceLevel, setEvidenceLevel] = useState('')

  const performSearch = async () => {
    if (!query.trim() || !systemInitialized || !apiConnected) return

    setIsSearching(true)
    
    try {
      let endpoint = '/search/enhanced'
      let requestBody = {
        query: query.trim(),
        top_k: topK,
        use_verification: useVerification
      }

      // Add filters if specified
      if (societyFilter) requestBody.society_filter = societyFilter
      if (yearFilter) requestBody.year_filter = yearFilter

      // Use clinical search if in clinical mode
      if (searchMode === 'clinical') {
        endpoint = '/search/clinical'
        requestBody = {
          question: query.trim(),
          patient_context: patientContext ? JSON.parse(`{${patientContext}}`) : null,
          evidence_level_required: evidenceLevel || null
        }
      }

      const response = await fetch(`${apiBaseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`)
      }

      const data = await response.json()
      setSearchResults(data)
      
      // Add to search history
      const historyItem = {
        query: query.trim(),
        timestamp: new Date().toISOString(),
        mode: searchMode,
        resultsCount: data.retrieval_results?.length || 0,
        verificationScore: data.verification?.overall_score || null,
        hallucination_risk: data.verification?.hallucination_risk || 'unknown'
      }
      setSearchHistory(prev => [historyItem, ...prev.slice(0, 9)]) // Keep last 10 searches

    } catch (error) {
      console.error('Search error:', error)
      setSearchResults({
        error: error.message,
        query: query.trim()
      })
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      performSearch()
    }
  }

  const getRiskBadgeColor = (risk) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'critical': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getVerificationIcon = (score) => {
    if (score >= 0.9) return <CheckCircle className="w-4 h-4 text-green-600" />
    if (score >= 0.7) return <AlertTriangle className="w-4 h-4 text-yellow-600" />
    return <AlertTriangle className="w-4 h-4 text-red-600" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl">
            <Brain className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-gray-900">MedGraphRAG Search</h2>
            <p className="text-gray-600">Advanced medical guideline search with verification</p>
          </div>
        </div>
      </motion.div>

      {/* Search Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Target className="w-5 h-5" />
            <span>Search Configuration</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search Mode Tabs */}
          <Tabs value={searchMode} onValueChange={setSearchMode}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="enhanced" className="flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>Enhanced Search</span>
              </TabsTrigger>
              <TabsTrigger value="clinical" className="flex items-center space-x-2">
                <Activity className="w-4 h-4" />
                <span>Clinical Query</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="enhanced" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch 
                    id="verification" 
                    checked={useVerification} 
                    onCheckedChange={setUseVerification}
                  />
                  <Label htmlFor="verification" className="flex items-center space-x-1">
                    <Shield className="w-4 h-4" />
                    <span>Reverse RAG Verification</span>
                  </Label>
                </div>
                
                <div className="space-y-2">
                  <Label>Results Count</Label>
                  <Select value={topK.toString()} onValueChange={(value) => setTopK(parseInt(value))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5">5 results</SelectItem>
                      <SelectItem value="10">10 results</SelectItem>
                      <SelectItem value="15">15 results</SelectItem>
                      <SelectItem value="20">20 results</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Society Filter</Label>
                  <Select value={societyFilter} onValueChange={setSocietyFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All societies" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All societies</SelectItem>
                      <SelectItem value="ESC">ESC</SelectItem>
                      <SelectItem value="ACC_AHA">ACC/AHA</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="clinical" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Patient Context (JSON format)</Label>
                  <Textarea
                    placeholder='e.g., "age": 65, "conditions": ["heart failure"], "medications": ["metoprolol"]'
                    value={patientContext}
                    onChange={(e) => setPatientContext(e.target.value)}
                    className="min-h-[80px]"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Evidence Level Required</Label>
                  <Select value={evidenceLevel} onValueChange={setEvidenceLevel}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any evidence level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Any evidence level</SelectItem>
                      <SelectItem value="Class I">Class I (Strong)</SelectItem>
                      <SelectItem value="Class IIa">Class IIa (Moderate)</SelectItem>
                      <SelectItem value="Class IIb">Class IIb (Weak)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Search Interface */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex space-x-4">
            <div className="flex-1">
              <Input
                placeholder={searchMode === 'clinical' 
                  ? "Enter your clinical question..." 
                  : "Search cardiovascular guidelines..."
                }
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={!systemInitialized || !apiConnected}
                className="text-lg py-3"
              />
            </div>
            <Button
              onClick={performSearch}
              disabled={!query.trim() || isSearching || !systemInitialized || !apiConnected}
              className="px-8 py-3"
            >
              {isSearching ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Search className="w-5 h-5" />
                </motion.div>
              ) : (
                <Search className="w-5 h-5" />
              )}
              <span className="ml-2">Search</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Search Results */}
      <AnimatePresence>
        {searchResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {searchResults.error ? (
              <Alert className="border-red-200 bg-red-50">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  <strong>Search Error:</strong> {searchResults.error}
                </AlertDescription>
              </Alert>
            ) : (
              <>
                {/* Search Summary */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Search Results</span>
                      <div className="flex items-center space-x-2">
                        {searchResults.verification && (
                          <Badge className={getRiskBadgeColor(searchResults.verification.hallucination_risk)}>
                            {getVerificationIcon(searchResults.verification.overall_score)}
                            <span className="ml-1">
                              Risk: {searchResults.verification.hallucination_risk}
                            </span>
                          </Badge>
                        )}
                        <Badge variant="outline">
                          {searchResults.retrieval_results?.length || 0} results
                        </Badge>
                      </div>
                    </CardTitle>
                    <CardDescription>
                      Query: "{searchResults.query}"
                      {searchResults.performance && (
                        <span className="ml-2 text-xs">
                          ({searchResults.performance.search_time_ms}ms)
                        </span>
                      )}
                    </CardDescription>
                  </CardHeader>
                  
                  {searchResults.response && (
                    <CardContent>
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
                          <Brain className="w-4 h-4 mr-2" />
                          AI-Generated Response
                        </h4>
                        <p className="text-blue-800 whitespace-pre-wrap">{searchResults.response}</p>
                      </div>
                    </CardContent>
                  )}
                </Card>

                {/* Verification Details */}
                {searchResults.verification && useVerification && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Shield className="w-5 h-5" />
                        <span>Verification Results</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {Math.round((searchResults.verification.overall_score || 0) * 100)}%
                          </div>
                          <div className="text-sm text-gray-600">Verification Score</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {searchResults.verification.verified_facts?.length || 0}
                          </div>
                          <div className="text-sm text-gray-600">Verified Facts</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">
                            {searchResults.verification.unverified_facts?.length || 0}
                          </div>
                          <div className="text-sm text-gray-600">Unverified Facts</div>
                        </div>
                      </div>
                      
                      {searchResults.verification.unverified_facts?.length > 0 && (
                        <Alert className="border-orange-200 bg-orange-50">
                          <AlertTriangle className="h-4 w-4 text-orange-600" />
                          <AlertDescription className="text-orange-800">
                            <strong>Unverified statements detected:</strong>
                            <ul className="list-disc list-inside mt-2">
                              {searchResults.verification.unverified_facts.slice(0, 3).map((fact, index) => (
                                <li key={index} className="text-sm">{fact}</li>
                              ))}
                            </ul>
                          </AlertDescription>
                        </Alert>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Retrieved Chunks */}
                {searchResults.retrieval_results && searchResults.retrieval_results.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <FileText className="w-5 h-5" />
                        <span>Source Documents</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {searchResults.retrieval_results.map((result, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <h4 className="font-semibold text-gray-900">
                                  {result.source || 'Unknown Source'}
                                </h4>
                                <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                                  <span>Page {result.page || 'N/A'}</span>
                                  <span>Score: {(result.score || 0).toFixed(3)}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {result.method || 'hybrid'}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                            <p className="text-gray-700 text-sm leading-relaxed">
                              {result.text}
                            </p>
                          </motion.div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search History */}
      {searchHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Recent Searches</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {searchHistory.slice(0, 5).map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => setQuery(item.query)}
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.query}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-600 mt-1">
                      <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                      <span>{item.resultsCount} results</span>
                      <Badge variant="outline" className="text-xs">
                        {item.mode}
                      </Badge>
                      {item.verificationScore && (
                        <Badge className={getRiskBadgeColor(item.hallucination_risk)}>
                          {Math.round(item.verificationScore * 100)}%
                        </Badge>
                      )}
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Search className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Status */}
      {!systemInitialized && (
        <Alert className="border-yellow-200 bg-yellow-50">
          <AlertTriangle className="h-4 w-4 text-yellow-600" />
          <AlertDescription className="text-yellow-800">
            System is not initialized. Please initialize the system before searching.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}

export default MedGraphSearchInterface

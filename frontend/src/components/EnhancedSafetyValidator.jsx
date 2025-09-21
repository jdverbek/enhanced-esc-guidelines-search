import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Heart, 
  Pill, 
  User, 
  Clock,
  Activity,
  Eye,
  Zap,
  FileText
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Separator } from '@/components/ui/separator.jsx'

const EnhancedSafetyValidator = ({ systemInitialized, apiConnected, apiBaseUrl }) => {
  const [recommendation, setRecommendation] = useState('')
  const [isValidating, setIsValidating] = useState(false)
  const [validationResults, setValidationResults] = useState(null)
  const [validationHistory, setValidationHistory] = useState([])
  
  // Patient profile state
  const [patientProfile, setPatientProfile] = useState({
    age: '',
    gender: '',
    weight: '',
    conditions: '',
    medications: '',
    allergies: '',
    kidney_function: 'normal',
    liver_function: 'normal',
    pregnancy_status: false
  })
  
  // Validation options
  const [checkInteractions, setCheckInteractions] = useState(true)
  const [checkContraindications, setCheckContraindications] = useState(true)

  const performValidation = async () => {
    if (!recommendation.trim() || !systemInitialized || !apiConnected) return

    setIsValidating(true)
    
    try {
      // Prepare patient profile
      const profile = {
        age: patientProfile.age ? parseInt(patientProfile.age) : null,
        gender: patientProfile.gender || null,
        weight: patientProfile.weight ? parseFloat(patientProfile.weight) : null,
        conditions: patientProfile.conditions ? patientProfile.conditions.split(',').map(c => c.trim()) : [],
        medications: patientProfile.medications ? patientProfile.medications.split(',').map(m => m.trim()) : [],
        allergies: patientProfile.allergies ? patientProfile.allergies.split(',').map(a => a.trim()) : [],
        kidney_function: patientProfile.kidney_function,
        liver_function: patientProfile.liver_function,
        pregnancy_status: patientProfile.pregnancy_status
      }

      const requestBody = {
        recommendation: recommendation.trim(),
        patient_profile: profile,
        check_interactions: checkInteractions,
        check_contraindications: checkContraindications
      }

      const response = await fetch(`${apiBaseUrl}/safety/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`)
      }

      const data = await response.json()
      setValidationResults(data)
      
      // Add to validation history
      const historyItem = {
        recommendation: recommendation.trim(),
        timestamp: new Date().toISOString(),
        riskLevel: data.validation_result?.risk_level || 'unknown',
        safetyScore: data.validation_result?.overall_safety_score || 0,
        interactionsCount: data.validation_result?.drug_interactions?.length || 0,
        contraindicationsCount: data.validation_result?.contraindications?.length || 0
      }
      setValidationHistory(prev => [historyItem, ...prev.slice(0, 9)]) // Keep last 10 validations

    } catch (error) {
      console.error('Validation error:', error)
      setValidationResults({
        error: error.message,
        recommendation: recommendation.trim()
      })
    } finally {
      setIsValidating(false)
    }
  }

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'high': return 'text-orange-600 bg-orange-100'
      case 'critical': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return <CheckCircle className="w-5 h-5" />
      case 'medium': return <AlertTriangle className="w-5 h-5" />
      case 'high': return <AlertTriangle className="w-5 h-5" />
      case 'critical': return <XCircle className="w-5 h-5" />
      default: return <Activity className="w-5 h-5" />
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'moderate': return 'bg-yellow-100 text-yellow-800'
      case 'minor': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
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
          <div className="bg-gradient-to-r from-red-500 to-pink-600 p-3 rounded-xl">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Enhanced Safety Validator</h2>
            <p className="text-gray-600">Comprehensive medical safety validation with drug interactions</p>
          </div>
        </div>
      </motion.div>

      {/* Patient Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="w-5 h-5" />
            <span>Patient Profile</span>
          </CardTitle>
          <CardDescription>
            Enter patient information for personalized safety validation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="demographics" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="demographics">Demographics</TabsTrigger>
              <TabsTrigger value="medical">Medical History</TabsTrigger>
              <TabsTrigger value="medications">Medications</TabsTrigger>
            </TabsList>
            
            <TabsContent value="demographics" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Age</Label>
                  <Input
                    type="number"
                    placeholder="e.g., 65"
                    value={patientProfile.age}
                    onChange={(e) => setPatientProfile(prev => ({ ...prev, age: e.target.value }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Gender</Label>
                  <Select 
                    value={patientProfile.gender} 
                    onValueChange={(value) => setPatientProfile(prev => ({ ...prev, gender: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Weight (kg)</Label>
                  <Input
                    type="number"
                    placeholder="e.g., 70"
                    value={patientProfile.weight}
                    onChange={(e) => setPatientProfile(prev => ({ ...prev, weight: e.target.value }))}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Kidney Function</Label>
                  <Select 
                    value={patientProfile.kidney_function} 
                    onValueChange={(value) => setPatientProfile(prev => ({ ...prev, kidney_function: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="mild">Mild impairment</SelectItem>
                      <SelectItem value="moderate">Moderate impairment</SelectItem>
                      <SelectItem value="severe">Severe impairment</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Liver Function</Label>
                  <Select 
                    value={patientProfile.liver_function} 
                    onValueChange={(value) => setPatientProfile(prev => ({ ...prev, liver_function: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="mild">Mild impairment</SelectItem>
                      <SelectItem value="moderate">Moderate impairment</SelectItem>
                      <SelectItem value="severe">Severe impairment</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="medical" className="space-y-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Medical Conditions</Label>
                  <Textarea
                    placeholder="e.g., atrial fibrillation, heart failure, diabetes (comma-separated)"
                    value={patientProfile.conditions}
                    onChange={(e) => setPatientProfile(prev => ({ ...prev, conditions: e.target.value }))}
                    className="min-h-[80px]"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Allergies</Label>
                  <Textarea
                    placeholder="e.g., penicillin, aspirin, shellfish (comma-separated)"
                    value={patientProfile.allergies}
                    onChange={(e) => setPatientProfile(prev => ({ ...prev, allergies: e.target.value }))}
                    className="min-h-[60px]"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch 
                    id="pregnancy" 
                    checked={patientProfile.pregnancy_status} 
                    onCheckedChange={(checked) => setPatientProfile(prev => ({ ...prev, pregnancy_status: checked }))}
                  />
                  <Label htmlFor="pregnancy">Pregnant or potentially pregnant</Label>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="medications" className="space-y-4">
              <div className="space-y-2">
                <Label>Current Medications</Label>
                <Textarea
                  placeholder="e.g., warfarin 5mg daily, metoprolol 50mg twice daily (comma-separated)"
                  value={patientProfile.medications}
                  onChange={(e) => setPatientProfile(prev => ({ ...prev, medications: e.target.value }))}
                  className="min-h-[100px]"
                />
                <p className="text-sm text-gray-600">
                  Include medication name, dose, and frequency for better validation
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Validation Options */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5" />
            <span>Validation Options</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Switch 
                id="interactions" 
                checked={checkInteractions} 
                onCheckedChange={setCheckInteractions}
              />
              <Label htmlFor="interactions" className="flex items-center space-x-1">
                <Pill className="w-4 h-4" />
                <span>Check Drug Interactions</span>
              </Label>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch 
                id="contraindications" 
                checked={checkContraindications} 
                onCheckedChange={setCheckContraindications}
              />
              <Label htmlFor="contraindications" className="flex items-center space-x-1">
                <AlertTriangle className="w-4 h-4" />
                <span>Check Contraindications</span>
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommendation Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Clinical Recommendation</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Enter the clinical recommendation to validate (e.g., 'Start amiodarone 200mg daily for rhythm control')"
            value={recommendation}
            onChange={(e) => setRecommendation(e.target.value)}
            disabled={!systemInitialized || !apiConnected}
            className="min-h-[100px] text-lg"
          />
          
          <Button
            onClick={performValidation}
            disabled={!recommendation.trim() || isValidating || !systemInitialized || !apiConnected}
            className="w-full py-3 text-lg"
          >
            {isValidating ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <Shield className="w-5 h-5" />
              </motion.div>
            ) : (
              <Shield className="w-5 h-5" />
            )}
            <span className="ml-2">Validate Safety</span>
          </Button>
        </CardContent>
      </Card>

      {/* Validation Results */}
      <AnimatePresence>
        {validationResults && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {validationResults.error ? (
              <Alert className="border-red-200 bg-red-50">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  <strong>Validation Error:</strong> {validationResults.error}
                </AlertDescription>
              </Alert>
            ) : (
              <>
                {/* Overall Safety Assessment */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Safety Assessment</span>
                      <div className="flex items-center space-x-2">
                        <Badge className={getRiskColor(validationResults.validation_result?.risk_level)}>
                          {getRiskIcon(validationResults.validation_result?.risk_level)}
                          <span className="ml-1">
                            {validationResults.validation_result?.risk_level?.toUpperCase() || 'UNKNOWN'} RISK
                          </span>
                        </Badge>
                      </div>
                    </CardTitle>
                    <CardDescription>
                      Recommendation: "{validationResults.recommendation}"
                    </CardDescription>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-600">
                          {Math.round((validationResults.validation_result?.overall_safety_score || 0) * 100)}%
                        </div>
                        <div className="text-sm text-gray-600">Safety Score</div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-red-600">
                          {validationResults.validation_result?.drug_interactions?.length || 0}
                        </div>
                        <div className="text-sm text-gray-600">Drug Interactions</div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-orange-600">
                          {validationResults.validation_result?.contraindications?.length || 0}
                        </div>
                        <div className="text-sm text-gray-600">Contraindications</div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-purple-600">
                          {validationResults.validation_result?.dosing_alerts?.length || 0}
                        </div>
                        <div className="text-sm text-gray-600">Dosing Alerts</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Drug Interactions */}
                {validationResults.validation_result?.drug_interactions?.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2 text-red-700">
                        <Pill className="w-5 h-5" />
                        <span>Drug Interactions</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {validationResults.validation_result.drug_interactions.map((interaction, index) => (
                          <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <h4 className="font-semibold text-red-900">
                                  {interaction.drug1} + {interaction.drug2}
                                </h4>
                                <Badge className={getSeverityColor(interaction.severity)}>
                                  {interaction.severity} severity
                                </Badge>
                              </div>
                            </div>
                            <p className="text-red-800 mb-2">
                              <strong>Effect:</strong> {interaction.clinical_effect}
                            </p>
                            <p className="text-red-700 mb-2">
                              <strong>Mechanism:</strong> {interaction.mechanism}
                            </p>
                            <p className="text-red-700">
                              <strong>Management:</strong> {interaction.management}
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Contraindications */}
                {validationResults.validation_result?.contraindications?.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2 text-orange-700">
                        <XCircle className="w-5 h-5" />
                        <span>Contraindications</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {validationResults.validation_result.contraindications.map((contraindication, index) => (
                          <div key={index} className="border border-orange-200 rounded-lg p-4 bg-orange-50">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <h4 className="font-semibold text-orange-900">
                                  {contraindication.medication} in {contraindication.condition}
                                </h4>
                                <Badge className={contraindication.contraindication_type === 'absolute' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}>
                                  {contraindication.contraindication_type} contraindication
                                </Badge>
                              </div>
                            </div>
                            <p className="text-orange-800 mb-2">
                              <strong>Reason:</strong> {contraindication.reason}
                            </p>
                            <p className="text-orange-700">
                              <strong>Alternatives:</strong> {contraindication.alternative_options?.join(', ') || 'None specified'}
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Safety Warnings and Recommendations */}
                {(validationResults.validation_result?.safety_warnings?.length > 0 || 
                  validationResults.validation_result?.recommendations?.length > 0) && (
                  <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Shield className="h-5 w-5 text-green-600" />
                          <span>Safety Guidance</span>
                        </CardTitle>
                      </CardHeader>
                    <CardContent className="space-y-4">
                      {validationResults.validation_result.safety_warnings?.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-red-700 mb-2">Warnings:</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {validationResults.validation_result.safety_warnings.map((warning, index) => (
                              <li key={index} className="text-red-600">{warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {validationResults.validation_result.recommendations?.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-blue-700 mb-2">Recommendations:</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {validationResults.validation_result.recommendations.map((rec, index) => (
                              <li key={index} className="text-blue-600">{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {validationResults.validation_result.requires_monitoring?.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-purple-700 mb-2">Monitoring Required:</h4>
                          <ul className="list-disc list-inside space-y-1">
                            {validationResults.validation_result.requires_monitoring.map((monitor, index) => (
                              <li key={index} className="text-purple-600">{monitor}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Validation History */}
      {validationHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Recent Validations</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {validationHistory.slice(0, 5).map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => setRecommendation(item.recommendation)}
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 truncate">{item.recommendation}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-600 mt-1">
                      <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                      <Badge className={getRiskColor(item.riskLevel)}>
                        {item.riskLevel}
                      </Badge>
                      <span>{Math.round(item.safetyScore * 100)}% safe</span>
                      {item.interactionsCount > 0 && (
                        <span className="text-red-600">{item.interactionsCount} interactions</span>
                      )}
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Eye className="w-4 h-4" />
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
            System is not initialized. Please initialize the system before using safety validation.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}

export default EnhancedSafetyValidator

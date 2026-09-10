import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { submitVerification } from '../services/experts'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { token } = useAuth()
  const [profile, setProfile] = useState<any>(null)
  const [documents, setDocuments] = useState<any[]>([])
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    experience_years: 0,
    hourly_rate: 0,
    bio: '',
  })
  const [resubmitOpen, setResubmitOpen] = useState(false)
  const [resubmitData, setResubmitData] = useState({
    experience_years: 0,
    linkedin_url: '',
    certificate_url: '',
    resume_url: '',
    notes: '',
  })
  const [uploading, setUploading] = useState(false)
  const [submittingVerification, setSubmittingVerification] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [file, setFile] = useState<File | null>(null)

  useEffect(() => {
    if (!token) {
      navigate('/login')
    } else {
      loadProfile()
    }
  }, [token, navigate])

  const loadProfile = async () => {
    try {
      const resp = await api.get('/auth/profile')
      setProfile(resp.data)
      if (resp.data.expert_profile) {
        setFormData({
          title: resp.data.expert_profile.title || '',
          company: resp.data.expert_profile.company || '',
          experience_years: resp.data.expert_profile.experience_years || 0,
          hourly_rate: resp.data.expert_profile.hourly_rate || 0,
          bio: resp.data.expert_profile.bio || '',
        })
        setResubmitData(prev => ({
          ...prev,
          experience_years: resp.data.expert_profile.experience_years || 0,
        }))
        loadDocuments(resp.data.expert_profile.id)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load profile')
    }
  }

  const loadDocuments = async (expertId: number) => {
    try {
      const resp = await api.get(`/documents/list/${expertId}`)
      setDocuments(resp.data)
    } catch (err) {
      console.error('Failed to load documents')
    }
  }

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const resp = await api.put('/experts/update', formData)
      setProfile({ ...profile, expert_profile: resp.data })
      setEditing(false)
      setSuccess('Profile updated successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile')
    }
  }

  const handleResubmitVerification = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmittingVerification(true)
    setError('')
    try {
      await submitVerification(resubmitData)
      setSuccess('Verification request submitted successfully! An administrator will review your credentials.')
      setResubmitOpen(false)
      await loadProfile()
      setTimeout(() => setSuccess(''), 4000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit verification request.')
    } finally {
      setSubmittingVerification(false)
    }
  }

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || !profile?.expert_profile?.id) return

    setUploading(true)
    const formDataToSend = new FormData()
    formDataToSend.append('expert_id', profile.expert_profile.id)
    formDataToSend.append('file', file)

    try {
      await api.post('/documents/upload-file', formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setFile(null)
      setSuccess('Document uploaded successfully!')
      setTimeout(() => setSuccess(''), 3000)
      loadDocuments(profile.expert_profile.id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteDocument = async (docId: number) => {
    try {
      await api.delete(`/documents/delete/${docId}`)
      setSuccess('Document deleted')
      setTimeout(() => setSuccess(''), 2000)
      loadDocuments(profile.expert_profile.id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  if (!profile) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
          <p className="mt-3 text-slate-600 font-medium">Loading profile...</p>
        </div>
      </div>
    )
  }

  const expert = profile.expert_profile

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">My Profile</h1>
          <p className="mt-1 text-sm text-slate-500">Manage your personal credentials, public identity, and documentation</p>
        </div>
        <span className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-1 text-xs font-semibold uppercase tracking-wider ${
          profile.is_admin ? 'bg-purple-100 text-purple-700' : profile.is_expert ? 'bg-indigo-100 text-indigo-700' : 'bg-emerald-100 text-emerald-700'
        }`}>
          {profile.is_admin ? 'Administrator' : profile.is_expert ? 'Expert Contributor' : 'Verified Learner'}
        </span>
      </div>

      {error && (
        <div className="mt-6 rounded-2xl bg-red-50 p-4 border border-red-200 text-sm text-red-700">
          ⚠️ {error}
        </div>
      )}
      {success && (
        <div className="mt-6 rounded-2xl bg-emerald-50 p-4 border border-emerald-200 text-sm text-emerald-700">
          ✓ {success}
        </div>
      )}

      {/* Account Info */}
      <div className="mt-8 rounded-3xl bg-white p-8 shadow-sm border border-slate-100">
        <h2 className="text-lg font-semibold text-slate-900">Account Information</h2>
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Full Name</p>
            <p className="mt-1 text-base font-semibold text-slate-900">{profile.name}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Email Address</p>
            <p className="mt-1 text-base font-semibold text-slate-900">{profile.email}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Primary Role</p>
            <p className="mt-1 text-base font-semibold capitalize text-slate-900">
              {profile.is_admin ? 'Admin' : profile.is_expert ? 'Expert' : 'Learner'}
            </p>
          </div>
        </div>
      </div>

      {/* Expert Profile & Verification Workflow */}
      {expert && (
        <div className="mt-8 rounded-3xl bg-white p-8 shadow-sm border border-slate-100">
          {/* Verification Status Banner */}
          <div className="mb-8">
            {expert.is_verified ? (
              <div className="rounded-2xl bg-emerald-50 border border-emerald-200 p-5 flex items-start gap-3">
                <div className="rounded-full bg-emerald-100 p-2 text-emerald-600 text-lg">✓</div>
                <div>
                  <h3 className="text-base font-semibold text-emerald-900">Verified Expert Status: ACTIVE</h3>
                  <p className="mt-1 text-sm text-emerald-700">
                    Your expert credentials have been approved by the administrative committee. Your profile is publicly listed on the Experts Directory and available for instant bookings.
                  </p>
                </div>
              </div>
            ) : expert.verification_status === 'rejected' ? (
              <div className="rounded-2xl bg-red-50 border border-red-200 p-5">
                <div className="flex items-start gap-3">
                  <div className="rounded-full bg-red-100 p-2 text-red-600 text-lg">✕</div>
                  <div className="flex-1">
                    <h3 className="text-base font-semibold text-red-900">Verification Rejected</h3>
                    <p className="mt-1 text-sm text-red-700">
                      Reason from administrator: <span className="font-medium italic">"{expert.rejection_reason || 'Please provide updated certificates or professional credentials.'}"</span>
                    </p>
                    <button
                      onClick={() => setResubmitOpen(!resubmitOpen)}
                      className="mt-3 inline-flex items-center gap-2 rounded-xl bg-red-600 px-4 py-2 text-xs font-semibold text-white hover:bg-red-700 shadow-sm"
                    >
                      {resubmitOpen ? 'Close Resubmission Form' : 'Submit Re-Verification Application'}
                    </button>
                  </div>
                </div>

                {resubmitOpen && (
                  <form onSubmit={handleResubmitVerification} className="mt-5 pt-5 border-t border-red-200/60 space-y-4">
                    <h4 className="text-sm font-bold text-slate-800">Update Credentials for Committee Re-review</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-medium text-slate-700 mb-1">LinkedIn Profile URL</label>
                        <input
                          type="url"
                          placeholder="https://linkedin.com/in/username"
                          value={resubmitData.linkedin_url}
                          onChange={(e) => setResubmitData({ ...resubmitData, linkedin_url: e.target.value })}
                          className="w-full rounded-xl border border-slate-300 p-2.5 text-sm outline-none focus:border-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-700 mb-1">Certificate / Portfolio Link</label>
                        <input
                          type="url"
                          placeholder="https://example.com/certificate.pdf"
                          value={resubmitData.certificate_url}
                          onChange={(e) => setResubmitData({ ...resubmitData, certificate_url: e.target.value })}
                          className="w-full rounded-xl border border-slate-300 p-2.5 text-sm outline-none focus:border-indigo-500"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1">Additional Notes for Reviewers</label>
                      <textarea
                        rows={3}
                        placeholder="Explain changes made or context regarding your certifications..."
                        value={resubmitData.notes}
                        onChange={(e) => setResubmitData({ ...resubmitData, notes: e.target.value })}
                        className="w-full rounded-xl border border-slate-300 p-2.5 text-sm outline-none focus:border-indigo-500"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={submittingVerification}
                      className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                    >
                      {submittingVerification ? 'Submitting...' : 'Submit for Committee Approval'}
                    </button>
                  </form>
                )}
              </div>
            ) : (
              <div className="rounded-2xl bg-amber-50 border border-amber-200 p-5 flex items-start gap-3">
                <div className="rounded-full bg-amber-100 p-2 text-amber-700 text-lg">⏳</div>
                <div className="flex-1">
                  <h3 className="text-base font-semibold text-amber-900">Verification Pending Administrator Review</h3>
                  <p className="mt-1 text-sm text-amber-800">
                    Your expert application has been submitted to the Admin Action Queue. Your profile is not publicly listed or bookable until an administrator reviews and approves your credentials.
                  </p>
                  <button
                    onClick={() => setResubmitOpen(!resubmitOpen)}
                    className="mt-3 text-xs font-semibold text-amber-900 underline hover:text-amber-700"
                  >
                    {resubmitOpen ? 'Hide Application Details' : 'View or update submitted credentials'}
                  </button>

                  {resubmitOpen && (
                    <form onSubmit={handleResubmitVerification} className="mt-4 pt-4 border-t border-amber-200/60 space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <input
                          type="url"
                          placeholder="LinkedIn URL"
                          value={resubmitData.linkedin_url}
                          onChange={(e) => setResubmitData({ ...resubmitData, linkedin_url: e.target.value })}
                          className="w-full rounded-xl border border-slate-300 p-2 text-sm"
                        />
                        <input
                          type="url"
                          placeholder="Certificate URL"
                          value={resubmitData.certificate_url}
                          onChange={(e) => setResubmitData({ ...resubmitData, certificate_url: e.target.value })}
                          className="w-full rounded-xl border border-slate-300 p-2 text-sm"
                        />
                      </div>
                      <textarea
                        rows={2}
                        placeholder="Notes for the reviewer..."
                        value={resubmitData.notes}
                        onChange={(e) => setResubmitData({ ...resubmitData, notes: e.target.value })}
                        className="w-full rounded-xl border border-slate-300 p-2 text-sm"
                      />
                      <button
                        type="submit"
                        disabled={submittingVerification}
                        className="rounded-xl bg-amber-700 px-4 py-2 text-xs font-semibold text-white hover:bg-amber-800"
                      >
                        {submittingVerification ? 'Updating...' : 'Update Application'}
                      </button>
                    </form>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Professional Details</h2>
              <p className="text-xs text-slate-500">How you appear to prospective learners and students</p>
            </div>
            <button
              onClick={() => setEditing(!editing)}
              className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-indigo-600 hover:bg-indigo-50"
            >
              {editing ? 'Cancel' : 'Edit Details'}
            </button>
          </div>

          {!editing ? (
            <div className="mt-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-medium text-slate-500">Professional Title</p>
                  <p className="mt-1 text-base font-medium text-slate-900">{formData.title || 'Not specified'}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-500">Organization / Company</p>
                  <p className="mt-1 text-base font-medium text-slate-900">{formData.company || 'Not specified'}</p>
                </div>
              </div>

              <div>
                <p className="text-xs font-medium text-slate-500">Bio & Summary</p>
                <p className="mt-1 text-sm text-slate-700 whitespace-pre-wrap">{formData.bio || 'No bio provided yet.'}</p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-xs font-medium text-slate-500">Experience</p>
                  <p className="mt-1 text-base font-medium text-slate-900">{formData.experience_years} years</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-500">Consultation Rate</p>
                  <p className="mt-1 text-base font-medium text-slate-900">₹{formData.hourly_rate} / hour</p>
                </div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleUpdateProfile} className="mt-6 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-3.5 text-sm outline-none focus:border-indigo-500"
                  placeholder="e.g. Principal Cloud Solutions Architect"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Company / Institution</label>
                <input
                  type="text"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-3.5 text-sm outline-none focus:border-indigo-500"
                  placeholder="e.g. Google Cloud / Autonomous Systems Lab"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Bio</label>
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-3.5 text-sm outline-none focus:border-indigo-500"
                  placeholder="Summarize your technical specialties and mentoring focus..."
                  rows={4}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Experience (Years)</label>
                  <input
                    type="number"
                    value={formData.experience_years}
                    onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) || 0 })}
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-3.5 text-sm outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Hourly Consultation Rate (₹)</label>
                  <input
                    type="number"
                    value={formData.hourly_rate}
                    onChange={(e) => setFormData({ ...formData, hourly_rate: parseFloat(e.target.value) || 0 })}
                    className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-3.5 text-sm outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="rounded-full bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 shadow-sm"
              >
                Save Changes
              </button>
            </form>
          )}
        </div>
      )}

      {/* Documents & Portfolio with Approval Lifecycle */}
      {expert && (
        <div className="mt-8 rounded-3xl bg-white p-8 shadow-sm border border-slate-100">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Knowledge Documents & Certifications</h2>
              <p className="text-xs text-slate-500">Uploaded documents are embedded for AI RAG search once approved by admin</p>
            </div>
            <span className="text-xs font-medium text-slate-500">{documents.length} document(s)</span>
          </div>

          <form onSubmit={handleFileUpload} className="mt-6 space-y-4">
            <div className="rounded-2xl border-2 border-dashed border-slate-200 p-6 text-center hover:border-indigo-400 transition-colors">
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                accept=".pdf,.txt,.doc,.docx"
              />
              <p className="mt-2 text-xs text-slate-400">Supported formats: PDF, TXT, DOC, DOCX (Max 10MB)</p>
            </div>
            <button
              type="submit"
              disabled={!file || uploading}
              className="rounded-full bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {uploading ? 'Processing & Uploading...' : 'Upload New Document'}
            </button>
          </form>

          <div className="mt-8">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Uploaded Files & Audit Status</h3>
            <div className="mt-4 space-y-3">
              {documents.length === 0 ? (
                <p className="text-sm text-slate-400 italic">No documents uploaded yet.</p>
              ) : (
                documents.map((doc) => {
                  const docStatus = doc.status || 'approved'
                  return (
                    <div key={doc.id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-2xl bg-slate-50 p-4 border border-slate-100">
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-semibold text-slate-900">{doc.file_url || `Document #${doc.id}`}</p>
                          <span className={`rounded-md px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                            docStatus === 'approved'
                              ? 'bg-emerald-100 text-emerald-800'
                              : docStatus === 'rejected'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}>
                            {docStatus}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5">
                          Type: {doc.file_type || 'Unknown'} • Uploaded: {new Date(doc.uploaded_at || Date.now()).toLocaleDateString()}
                        </p>
                        {doc.review_notes && (
                          <p className="text-xs text-slate-600 mt-1 italic bg-white/80 p-1.5 rounded border border-slate-200">
                            Notes: {doc.review_notes}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="self-start sm:self-center text-xs font-medium text-red-600 hover:text-red-800 hover:underline"
                      >
                        Remove
                      </button>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  )
}

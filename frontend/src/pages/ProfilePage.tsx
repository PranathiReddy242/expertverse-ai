import { useState, useEffect } from 'react'
import api from '../services/api'

export default function ProfilePage() {
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
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [file, setFile] = useState<File | null>(null)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const resp = await api.get('/auth/profile')
      setProfile(resp.data)
      if (resp.data.expert_profile) {
        setFormData(resp.data.expert_profile)
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
      const resp = await api.put(`/experts/update/${profile.expert_profile.id}`, formData)
      setProfile({ ...profile, expert_profile: resp.data })
      setEditing(false)
      setSuccess('Profile updated successfully!')
      setTimeout(() => setSuccess(''), 2000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile')
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
      setTimeout(() => setSuccess(''), 2000)
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
      loadDocuments(profile.expert_profile.id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  if (!profile) {
    return <div className="p-8 text-center">Loading profile...</div>
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <h1 className="text-3xl font-semibold">My Profile</h1>

      {/* Basic Info */}
      <div className="mt-8 rounded-3xl bg-white p-10 shadow-lg">
        <h2 className="text-xl font-semibold">Account Information</h2>
        <div className="mt-6 space-y-4">
          <div>
            <p className="text-sm text-slate-600">Name</p>
            <p className="mt-1 text-lg font-medium">{profile.name}</p>
          </div>
          <div>
            <p className="text-sm text-slate-600">Email</p>
            <p className="mt-1 text-lg font-medium">{profile.email}</p>
          </div>
          <div>
            <p className="text-sm text-slate-600">Role</p>
            <p className="mt-1 text-lg font-medium capitalize">{profile.role}</p>
          </div>
        </div>
      </div>

      {/* Expert Profile */}
      {profile.expert_profile && (
        <div className="mt-8 rounded-3xl bg-white p-10 shadow-lg">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Expert Profile</h2>
            <button
              onClick={() => setEditing(!editing)}
              className="text-sm text-indigo-600 hover:underline"
            >
              {editing ? 'Cancel' : 'Edit'}
            </button>
          </div>

          {!editing ? (
            <div className="mt-6 space-y-4">
              <div>
                <p className="text-sm text-slate-600">Title</p>
                <p className="mt-1 text-lg font-medium">{formData.title}</p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Company</p>
                <p className="mt-1 text-lg font-medium">{formData.company}</p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Bio</p>
                <p className="mt-1 text-sm text-slate-700">{formData.bio}</p>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-slate-600">Experience (years)</p>
                  <p className="mt-1 text-lg font-medium">{formData.experience_years}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Hourly Rate ($)</p>
                  <p className="mt-1 text-lg font-medium">${formData.hourly_rate}</p>
                </div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleUpdateProfile} className="mt-6 space-y-4">
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                placeholder="Title"
              />
              <input
                type="text"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                className="w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                placeholder="Company"
              />
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                className="w-full rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                placeholder="Bio"
                rows={4}
              />
              <div className="grid gap-4 sm:grid-cols-2">
                <input
                  type="number"
                  value={formData.experience_years}
                  onChange={(e) => setFormData({ ...formData, experience_years: parseInt(e.target.value) })}
                  className="rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                  placeholder="Years"
                />
                <input
                  type="number"
                  value={formData.hourly_rate}
                  onChange={(e) => setFormData({ ...formData, hourly_rate: parseFloat(e.target.value) })}
                  className="rounded-3xl border border-slate-200 bg-slate-50 p-4 outline-none focus:border-indigo-500"
                  placeholder="Hourly Rate"
                />
              </div>
              <button className="rounded-full bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-700">
                Save Changes
              </button>
            </form>
          )}
        </div>
      )}

      {/* Documents */}
      {profile.expert_profile && (
        <div className="mt-8 rounded-3xl bg-white p-10 shadow-lg">
          <h2 className="text-xl font-semibold">Documents & Portfolio</h2>

          <form onSubmit={handleFileUpload} className="mt-6 space-y-4">
            <div className="rounded-3xl border-2 border-dashed border-slate-300 p-6">
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full"
                accept=".pdf,.txt,.doc,.docx"
              />
              <p className="mt-2 text-xs text-slate-500">PDF, TXT, DOC, DOCX supported</p>
            </div>
            <button
              type="submit"
              disabled={!file || uploading}
              className="rounded-full bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </form>

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-slate-700">Your Documents</h3>
            <div className="mt-4 space-y-2">
              {documents.length === 0 ? (
                <p className="text-sm text-slate-500">No documents yet</p>
              ) : (
                documents.map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between rounded-2xl bg-slate-50 p-4">
                    <div>
                      <p className="text-sm font-medium">{doc.file_url || `Document ${doc.id}`}</p>
                      <p className="text-xs text-slate-500">{doc.file_type}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteDocument(doc.id)}
                      className="text-sm text-red-600 hover:underline"
                    >
                      Delete
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      {success && <p className="mt-4 text-sm text-green-600">✓ {success}</p>}
    </main>
  )
}

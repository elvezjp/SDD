import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route, Navigate, useParams } from 'react-router'
import Layout from '../Layout'

/**
 * Smoke tests for the routing primitives used by App.tsx.
 *
 * App.tsx wires these together with BrowserRouter; here we swap in
 * MemoryRouter so routes can be exercised without a real browser history.
 * The route structure mirrors App.tsx so that a breaking change in
 * react-router surfaces here rather than only in the running app.
 */

function ProjectId() {
  const { projectId } = useParams()
  return <div>project: {projectId}</div>
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<div>dashboard content</div>} />
          <Route path="interview/:projectId" element={<ProjectId />} />
        </Route>
      </Routes>
    </MemoryRouter>
  )
}

describe('routing', () => {
  it('renders child routes through the Layout Outlet', () => {
    renderAt('/dashboard')
    expect(screen.getByText('dashboard content')).toBeInTheDocument()
    // Layout itself is rendered around the child route.
    expect(screen.getByText('Spec AIライター')).toBeInTheDocument()
  })

  it('redirects the index route to /dashboard', () => {
    renderAt('/')
    expect(screen.getByText('dashboard content')).toBeInTheDocument()
  })

  it('exposes route params via useParams', () => {
    renderAt('/interview/abcd1234')
    expect(screen.getByText('project: abcd1234')).toBeInTheDocument()
  })

  it('marks the active nav link based on the current location', () => {
    renderAt('/dashboard')
    const dashboardLink = screen.getByRole('link', { name: /ダッシュボード/ })
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    expect(dashboardLink.className).toContain('bg-primary-100')

    const settingsLink = screen.getByRole('link', { name: /設定/ })
    expect(settingsLink.className).not.toContain('bg-primary-100')
  })
})

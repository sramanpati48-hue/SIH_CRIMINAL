# Demo Manual Checklist

*Note: Automated browser testing is deferred. Use this checklist for manual verification of the demo.*

1. **Login & Authentication**
   - [ ] Navigate to the login page.
   - [ ] Log in with valid demo credentials.
   - [ ] Verify successful redirection to the dashboard.

2. **Case Navigation**
   - [ ] View the list of available synthetic cases.
   - [ ] Select a designated demo case and verify the case details load correctly.

3. **Graph Visualization**
   - [ ] Navigate to the Graph View.
   - [ ] Verify that nodes (entities) and edges (relationships) render correctly based on synthetic data.
   - [ ] Interact with the graph (zoom, pan, click nodes).

4. **Traceability and Evidence**
   - [ ] Click on a specific relationship (edge).
   - [ ] Verify that the side panel displays the source text, confidence score, and timestamp.

5. **Human-in-the-Loop Review**
   - [ ] Navigate to the Pending Extractions review screen.
   - [ ] Accept a pending relationship. Verify it updates in the graph.
   - [ ] Reject a pending relationship. Verify it is removed from active consideration.

6. **Analytics and Patterns**
   - [ ] Open the Analytics/Alerts pane.
   - [ ] Verify the system highlights an *investigative lead* or *pattern* (not a guilt prediction).

7. **Similarity Search**
   - [ ] Select an entity.
   - [ ] Execute a similarity or related-entity query.
   - [ ] Verify the results return logically connected synthetic entities.

8. **Export Button**
   - [ ] Click the "Export Report" button.
   - [ ] Verify a document (PDF/CSV/JSON) is generated containing the verified leads and traceability data.

9. **Role Visibility & Access Denied**
   - [ ] Log out and log back in with a restricted role (e.g., Read-Only Analyst).
   - [ ] Attempt to accept/reject an extraction or access admin settings.
   - [ ] Verify an appropriate "Access Denied" or disabled UI state is presented.

10. **Synthetic Notices**
    - [ ] Verify that disclaimers stating "System uses synthetic data only" and "Not a guilt prediction" are visible in the UI.

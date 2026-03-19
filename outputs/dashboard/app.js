(function () {
  const data = window.DASHBOARD_DATA;
  if (!data) {
    document.body.innerHTML = "<p>Dashboard data failed to load.</p>";
    return;
  }

  const families = [...new Set(data.phase_path_divergence.map((row) => row.task_family))];
  const familySelect = document.getElementById("family-select");
  const outcomeFilter = document.getElementById("outcome-filter");

  const fmt = (value, digits = 3) => Number(value).toFixed(digits);

  function createOverviewCards() {
    const cards = [
      {
        label: "Temperature Run",
        value: data.overview.temperature_run.trace_count,
        meta: `${data.overview.temperature_run.step_count} steps / ${data.overview.temperature_run.delta_count} deltas`,
      },
      {
        label: "Repeated 8x5 Run",
        value: data.overview.repeated_8x5_run.trace_count,
        meta: `${data.overview.repeated_8x5_run.step_count} steps / ${data.overview.repeated_8x5_run.delta_count} deltas`,
      },
      {
        label: "Embedding Model",
        value: "MiniLM",
        meta: data.overview.embedding_model,
      },
      {
        label: "Top Finding Score",
        value: `${fmt(data.finding_scores[0].evidence_score, 1)}`,
        meta: data.finding_scores[0].finding,
      },
    ];

    const container = document.getElementById("overview-cards");
    container.innerHTML = cards
      .map(
        (card) => `
          <article class="metric-card">
            <div class="label">${card.label}</div>
            <div class="value">${card.value}</div>
            <div class="meta">${card.meta}</div>
          </article>
        `,
      )
      .join("");
  }

  function renderFindingScores() {
    const container = document.getElementById("finding-scores");
    container.innerHTML = `
      <div class="score-list">
        ${data.finding_scores
          .map(
            (row) => `
              <article class="score-card">
                <div class="score-header">
                  <div>
                    <div class="section-label">${row.finding_id}</div>
                    <h3>${row.finding}</h3>
                  </div>
                  <div class="score-pill">${fmt(row.evidence_score, 1)}/100</div>
                </div>
                <p class="muted">${row.notes}</p>
                <div class="bar-list">
                  ${barRow("Sample", row.sample_component, "blue")}
                  ${barRow("Effect", row.effect_component, "accent")}
                  ${barRow("Consistency", row.consistency_component, "green")}
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
    `;
  }

  function barRow(label, value, tone) {
    return `
      <div class="bar-row">
        <span>${label}</span>
        <div class="bar-track"><div class="bar-fill ${tone}" style="width:${Math.max(0, Math.min(1, Number(value))) * 100}%"></div></div>
        <strong>${fmt(value)}</strong>
      </div>
    `;
  }

  function renderFamilyOptions() {
    familySelect.innerHTML = families.map((family) => `<option value="${family}">${family}</option>`).join("");
  }

  function renderFamilyPanel() {
    const family = familySelect.value;
    const alignRows = data.alignment_summary.filter((row) => row.task_family === family);
    const residualRows = data.residual_summary.filter((row) => row.task_family === family);
    const pathRow = data.phase_path_divergence.find((row) => row.task_family === family);
    const predictRows = data.phase_predictability.filter((row) => row.task_family === family);
    const lateRows = data.late_cluster_predictability.filter((row) => row.task_family === family);
    const tempRow = data.temperature_family_margin.find((row) => row.task_family === family);

    document.getElementById("family-alignment").innerHTML = `
      <div class="bar-list">
        ${alignRows
          .map((row) => barRow(`${row.outcome} align`, row.best_abs_alignment, "accent"))
          .join("")}
        ${residualRows
          .map((row) => barRow(`${row.outcome} residual`, row.residual_norm_mean, "blue"))
          .join("")}
      </div>
    `;

    document.getElementById("family-phase-path").innerHTML = pathRow
      ? `
        <div class="stat-list">
          <div><span class="chip">Correct</span> ${pathRow.correct_dominant_path}</div>
          <div><span class="chip">Incorrect</span> ${pathRow.incorrect_dominant_path}</div>
          <div class="muted">Path JS divergence: ${fmt(pathRow.path_js_divergence)}</div>
        </div>
      `
      : "<p class='muted'>No path data.</p>";

    document.getElementById("family-predictability").innerHTML = `
      <div class="bar-list">
        ${predictRows
          .map((row) => barRow(`${row.feature_set}`, row.cv_balanced_accuracy, "green"))
          .join("")}
        ${lateRows
          .map((row) => barRow(`${row.feature_set} late`, row.late_cluster_rule_accuracy, "blue"))
          .join("")}
      </div>
    `;

    document.getElementById("family-temperature").innerHTML = tempRow
      ? `
        <div class="bar-list">
          ${barRow("Same temp JS", tempRow.same_temp_js, "accent")}
          ${barRow("Cross temp JS", tempRow.cross_temp_js, "blue")}
          ${barRow("Temp margin", Math.abs(tempRow.temperature_margin), "green")}
        </div>
        <p class="muted">Signed margin: ${fmt(tempRow.temperature_margin)}</p>
      `
      : "<p class='muted'>No temperature data.</p>";
  }

  function renderPromptSignificance() {
    const outcome = outcomeFilter.value;
    const rows = data.prompt_recurrence_significance
      .filter((row) => outcome === "all" || row.outcome === outcome)
      .sort((a, b) => a.permutation_p_value - b.permutation_p_value || b.observed_pairwise_margin - a.observed_pairwise_margin);

    document.getElementById("prompt-significance").innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Family</th>
            <th>Outcome</th>
            <th>Prompts</th>
            <th>Pairwise Margin</th>
            <th>P-Value</th>
            <th>Positive Prompt Share</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
                <tr>
                  <td>${row.task_family}</td>
                  <td>${row.outcome}</td>
                  <td>${row.n_prompts}</td>
                  <td>${fmt(row.observed_pairwise_margin)}</td>
                  <td>${Number(row.permutation_p_value).toFixed(3)}</td>
                  <td>${fmt(row.positive_prompt_share)}</td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    `;
  }

  function renderPhaseDivergenceTable() {
    const rows = [...data.step_phase_failure_divergence].sort((a, b) => b.js_divergence - a.js_divergence);
    document.getElementById("phase-divergence-table").innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Family</th>
            <th>Phase</th>
            <th>JS</th>
            <th>TV</th>
            <th>Correct Mode</th>
            <th>Incorrect Mode</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
                <tr>
                  <td>${row.task_family}</td>
                  <td>${row.phase}</td>
                  <td>${fmt(row.js_divergence)}</td>
                  <td>${fmt(row.tv_distance)}</td>
                  <td>${row.correct_mode_cluster}</td>
                  <td>${row.incorrect_mode_cluster}</td>
                </tr>
              `,
            )
            .join("")}
        </tbody>
      </table>
    `;
  }

  familySelect.addEventListener("change", renderFamilyPanel);
  outcomeFilter.addEventListener("change", renderPromptSignificance);

  createOverviewCards();
  renderFindingScores();
  renderFamilyOptions();
  renderFamilyPanel();
  renderPromptSignificance();
  renderPhaseDivergenceTable();
})();

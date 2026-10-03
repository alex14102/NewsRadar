package pl.fiszki.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import pl.fiszki.app.data.Stats
import pl.fiszki.app.data.dni
import pl.fiszki.app.ui.components.BottomBar
import pl.fiszki.app.ui.components.Headline
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.Panel
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.viewmodel.StatsViewModel

@Composable
fun StatsScreen(vm: StatsViewModel, onTab: (String) -> Unit) {
    val t = Fiszki.t
    val ui by vm.ui.collectAsStateWithLifecycle()
    val week = ui.week
    val max = (week.maxOfOrNull { it.count } ?: 1).coerceAtLeast(1)

    Box(Modifier.fillMaxSize()) {
        Column(
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 96.dp)
        ) {
            Column(Modifier.padding(start = 24.dp, end = 20.dp, top = 24.dp)) {
                MonoLabel("/PROC/STATS", decorative = true)
                Headline("Statystyki", size = 38)
            }
            Row(Modifier.padding(20.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Column(
                    Modifier
                        .weight(1f)
                        .clip(t.shape(18.dp))
                        .background(t.accent)
                        .padding(16.dp)
                ) {
                    MonoLabel("STREAK", color = t.onAccent, size = 10, bold = true)
                    Headline(dni(ui.streak), size = 44, color = t.onAccent)
                }
                Panel(Modifier.weight(1f), cut = 18.dp) {
                    MonoLabel("SKUTECZNOŚĆ 7 DNI", size = 10)
                    Headline(ui.retentionWeek.percent(), size = 44, color = t.c.primary)
                }
            }

            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom,
            ) {
                Headline("Ostatnie 7 dni", size = 22)
                MonoLabel("KARTY/DZIEŃ")
            }
            Row(
                Modifier
                    .fillMaxWidth()
                    .height(210.dp)
                    .padding(horizontal = 20.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.Bottom,
            ) {
                week.forEach { (day, n, today) ->
                    Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                        MonoLabel("$n", size = 10)
                        Spacer(Modifier.height(4.dp))
                        Box(
                            Modifier
                                .fillMaxWidth()
                                .height((140f * n / max).coerceAtLeast(2f).dp)
                                .clip(t.shape(6.dp))
                                .background(if (today) t.accent else t.c.primary)
                        )
                        Spacer(Modifier.height(6.dp))
                        MonoLabel(day, size = 10)
                    }
                }
            }

            Column(Modifier.padding(horizontal = 20.dp, vertical = 8.dp)) {
                listOf(
                    "Wszystkie karty" to "${ui.totalCards}",
                    "Opanowane (≥${Stats.MASTERED_DAYS} dni)" to "${ui.mastered}",
                    "Powtórzone dziś" to "${ui.reviewedToday}",
                    "Skuteczność dziś" to ui.retentionToday.percent(),
                    "Powtórki łącznie" to "${ui.reviewsAllTime}",
                ).forEach { (k, v) ->
                    Box(Modifier.fillMaxWidth().height(1.dp).background(t.c.line))
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .heightIn(min = 48.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(k, fontSize = 15.sp, fontWeight = FontWeight.Medium)
                        MonoLabel(v, color = t.accent, size = 13, bold = true)
                    }
                }
                Box(Modifier.fillMaxWidth().height(1.dp).background(t.c.line))
            }
        }
        BottomBar("stats", onTab, Modifier.align(Alignment.BottomCenter))
    }
}

private fun Int?.percent() = if (this == null) "—" else "$this%"

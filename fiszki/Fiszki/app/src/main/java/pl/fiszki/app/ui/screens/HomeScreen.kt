package pl.fiszki.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import pl.fiszki.app.data.Repository
import pl.fiszki.app.ui.components.BottomBar
import pl.fiszki.app.ui.components.CyberButton
import pl.fiszki.app.ui.components.Hatch
import pl.fiszki.app.ui.components.Headline
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.Panel
import pl.fiszki.app.ui.components.SegmentBar
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.Fonts

@Composable
fun HomeScreen(
    repo: Repository,
    onStudy: (Long) -> Unit,
    onAdd: () -> Unit,
    onTab: (String) -> Unit,
) {
    val t = Fiszki.t
    val now = System.currentTimeMillis()
    val dueAll = repo.due(null, now).size
    val done = repo.reviewedToday
    val progress = if (done + dueAll == 0) 1f else done.toFloat() / (done + dueAll)

    Box(Modifier.fillMaxSize()) {
        Column(
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(bottom = 170.dp)
        ) {
            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(start = 24.dp, end = 20.dp, top = 24.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top,
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    MonoLabel("SYS://FISZKI_v0.1", decorative = true)
                    Headline("Twoje fiszki", size = 38)
                }
                Column(
                    Modifier
                        .clip(t.shape(12.dp))
                        .background(t.accent)
                        .padding(horizontal = 14.dp, vertical = 8.dp),
                    horizontalAlignment = Alignment.End,
                ) {
                    MonoLabel("STREAK", color = t.onAccent, size = 9, bold = true)
                    Headline("${repo.streakDays} dni", size = 24, color = t.onAccent)
                }
            }

            // Kolejka na dziś
            Column(
                Modifier
                    .padding(20.dp)
                    .fillMaxWidth()
                    .clip(t.shape(22.dp))
                    .background(t.c.primary)
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    MonoLabel("_QUEUE.TODAY", color = t.c.onPrimary, bold = true)
                    MonoLabel("[$done/${done + dueAll}]", color = t.c.onPrimary, bold = true)
                }
                Headline("$dueAll kart", size = 56, color = t.c.onPrimary)
                SegmentBar(progress, t.c.onPrimary)
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    CyberButton(
                        "▶ START_SESJI",
                        onClick = { onStudy(-1L) },
                        bg = t.c.onPrimary,
                        fg = t.accent,
                        enabled = dueAll > 0,
                        cut = 10.dp,
                    )
                    Hatch(Modifier.size(64.dp, 22.dp), color = t.c.onPrimary)
                }
            }

            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(start = 24.dp, end = 20.dp, top = 4.dp, bottom = 10.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom,
            ) {
                Headline("Talie", size = 24)
                MonoLabel("/DECKS [%02d]".format(repo.decks.size), decorative = true)
            }

            Column(
                Modifier.padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                repo.decks.forEach { d ->
                    val total = repo.cards.count { it.deckId == d.id }
                    val due = repo.due(d.id, now).size
                    Panel(
                        Modifier.fillMaxWidth(),
                        padding = PaddingValues(horizontal = 14.dp, vertical = 12.dp),
                        onClick = { onStudy(d.id) },
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            MonoLabel("[${d.short}]", Modifier.width(56.dp), color = t.c.primary, size = 12, bold = true)
                            Column(Modifier.weight(1f)) {
                                Text(
                                    d.name.uppercase(),
                                    fontFamily = Fonts.Display,
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 19.sp,
                                )
                                MonoLabel("$total KART // ${d.path}")
                            }
                            Box(
                                Modifier
                                    .background(t.accent)
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                MonoLabel("$due", color = t.onAccent, size = 13, bold = true)
                            }
                        }
                    }
                }
            }
        }

        // FAB: nowa fiszka
        Box(
            Modifier
                .align(Alignment.BottomEnd)
                .padding(end = 20.dp, bottom = 96.dp)
                .size(58.dp)
                .clip(t.shape(14.dp))
                .background(t.accent)
                .clickable(role = Role.Button, onClick = onAdd)
                .semantics { contentDescription = "Dodaj fiszkę" },
            contentAlignment = Alignment.Center,
        ) {
            Text("+", color = t.onAccent, fontSize = 30.sp, fontWeight = FontWeight.Bold)
        }

        BottomBar("home", onTab, Modifier.align(Alignment.BottomCenter))
    }
}

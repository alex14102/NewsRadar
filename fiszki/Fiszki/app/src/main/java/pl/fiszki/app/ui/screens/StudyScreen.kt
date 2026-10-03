package pl.fiszki.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.toMutableStateList
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import pl.fiszki.app.data.Rating
import pl.fiszki.app.data.Repository
import pl.fiszki.app.data.Srs
import pl.fiszki.app.ui.components.CyberButton
import pl.fiszki.app.ui.components.Hatch
import pl.fiszki.app.ui.components.Headline
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.Panel
import pl.fiszki.app.ui.components.TopBar
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.Fonts

/** deckId = -1 → wszystkie talie. */
@Composable
fun StudyScreen(repo: Repository, deckId: Long, onBack: () -> Unit) {
    val t = Fiszki.t
    val queue = remember {
        repo.due(deckId.takeIf { it >= 0 }, System.currentTimeMillis()).map { it.id }.toMutableStateList()
    }
    val total = remember { queue.size }
    var flipped by remember { mutableStateOf(false) }
    val card = queue.firstOrNull()?.let { id -> repo.cards.firstOrNull { it.id == id } }
    val deck = repo.decks.firstOrNull { it.id == deckId }
    val doneCount = (total - queue.size).coerceAtLeast(0)

    Column(Modifier.fillMaxSize()) {
        TopBar(
            title = deck?.name ?: "Wszystkie talie",
            sub = deck?.path ?: "/ALL",
            onBack = onBack,
            trailing = if (total > 0) "${(doneCount + 1).coerceAtMost(total)}/$total" else null,
        )
        Box(
            Modifier
                .padding(horizontal = 20.dp, vertical = 12.dp)
                .fillMaxWidth()
                .height(4.dp)
                .background(t.c.raised)
        ) {
            Box(
                Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(if (total == 0) 1f else doneCount.toFloat() / total)
                    .background(t.accent)
            )
        }

        if (card == null) {
            Column(
                Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(24.dp),
                verticalArrangement = Arrangement.Center,
            ) {
                MonoLabel("_SESSION.END", color = t.c.primary, bold = true)
                Headline("Wszystko powtórzone", size = 44)
                Spacer(Modifier.height(8.dp))
                Text("Wróć później po kolejne karty.", color = t.c.muted, fontSize = 16.sp)
            }
            CyberButton(
                "WRÓĆ_DO_TALII", onBack,
                Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
            )
        } else {
            Panel(
                Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp),
                cut = 28.dp,
                padding = PaddingValues(0.dp),
            ) {
                Row(
                    Modifier
                        .fillMaxWidth()
                        .padding(start = 28.dp, end = 18.dp, top = 24.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    MonoLabel("_FRONT", decorative = true)
                    Hatch(Modifier.size(48.dp, 14.dp))
                }
                Column(
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp),
                    verticalArrangement = Arrangement.Center,
                ) {
                    Headline(card.front, size = t.settings.textSize.wordSp)
                    if (card.ipa.isNotBlank()) MonoLabel(card.ipa, color = t.c.primary, size = 14)
                }
                if (flipped) {
                    Column(
                        Modifier
                            .padding(12.dp)
                            .fillMaxWidth()
                            .clip(t.shape(18.dp))
                            .background(t.c.primary)
                            .padding(18.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        MonoLabel("_BACK", color = t.c.onPrimary, bold = true)
                        Headline(card.back, size = 32, color = t.c.onPrimary)
                        if (card.example.isNotBlank()) {
                            Text(card.example, color = t.c.onPrimary, fontSize = 15.sp, fontStyle = FontStyle.Italic)
                        }
                    }
                }
            }

            Box(
                Modifier
                    .fillMaxWidth()
                    .padding(20.dp)
            ) {
                if (!flipped) {
                    CyberButton("POKAŻ_ODPOWIEDŹ", { flipped = true }, Modifier.fillMaxWidth(), cut = 14.dp)
                } else {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Rating.entries.forEach { r ->
                            val (bg, fg) = when (r) {
                                Rating.AGAIN, Rating.HARD -> t.c.raised to t.c.ink
                                Rating.GOOD -> t.c.primary to t.c.onPrimary
                                Rating.EASY -> t.accent to t.onAccent
                            }
                            Column(
                                Modifier
                                    .weight(1f)
                                    .heightIn(min = 64.dp)
                                    .clip(t.shape(10.dp))
                                    .background(bg)
                                    .clickable(role = Role.Button) {
                                        repo.rate(card, r)
                                        queue.removeAt(0)
                                        if (r == Rating.AGAIN) queue.add(card.id)
                                        flipped = false
                                    },
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center,
                            ) {
                                Text(r.label, color = fg, fontFamily = Fonts.Display, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                                Text(Srs.previewLabel(card, r), color = fg, fontFamily = Fonts.Mono, fontSize = 11.sp)
                            }
                        }
                    }
                }
            }
        }
    }
}

package pl.fiszki.app.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import pl.fiszki.app.data.Card
import pl.fiszki.app.data.kart
import pl.fiszki.app.ui.components.ConfirmDialog
import pl.fiszki.app.ui.components.CyberButton
import pl.fiszki.app.ui.components.DeckFormDialog
import pl.fiszki.app.ui.components.Headline
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.Panel
import pl.fiszki.app.ui.components.TopBar
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.theme.Fonts
import pl.fiszki.app.ui.viewmodel.DeckViewModel

/** Talia: lista kart (stuknięcie = edycja, × = usuń), nauka, zmiana nazwy, usunięcie talii. */
@Composable
fun DeckScreen(
    vm: DeckViewModel,
    onBack: () -> Unit,
    onStudy: (Long) -> Unit,
    onAddCard: (deckId: Long) -> Unit,
    onEditCard: (cardId: Long) -> Unit,
) {
    val t = Fiszki.t
    val ui by vm.ui.collectAsStateWithLifecycle()
    val deck = ui.deck
    var rename by remember { mutableStateOf(false) }
    var deleteDeck by remember { mutableStateOf(false) }
    var deleteCard by remember { mutableStateOf<Card?>(null) }

    // Talia zniknęła (np. usunięta) — wracamy.
    LaunchedEffect(ui.loaded, deck) { if (ui.loaded && deck == null) onBack() }
    if (deck == null) return

    Box(Modifier.fillMaxSize()) {
        LazyColumn(
            Modifier.fillMaxSize(),
            contentPadding = PaddingValues(bottom = 110.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            item {
                TopBar(title = deck.name, sub = deck.path, onBack = onBack, trailing = "[${deck.short}]")
            }
            item {
                Column(
                    Modifier
                        .padding(horizontal = 20.dp, vertical = 8.dp)
                        .fillMaxWidth()
                        .clip(t.shape(22.dp))
                        .background(t.c.primary)
                        .padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        MonoLabel("_DECK.STATUS", color = t.c.onPrimary, bold = true)
                        MonoLabel("[${ui.due}/${ui.cards.size}]", color = t.c.onPrimary, bold = true)
                    }
                    Headline("${kart(ui.due)} na dziś", size = 40, color = t.c.onPrimary)
                    CyberButton(
                        "▶ UCZ_SIĘ",
                        onClick = { onStudy(deck.id) },
                        modifier = Modifier.fillMaxWidth(),
                        bg = t.c.onPrimary,
                        fg = t.accent,
                        enabled = ui.due > 0,
                        cut = 10.dp,
                    )
                }
            }
            item {
                Row(
                    Modifier.padding(horizontal = 20.dp),
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    CyberButton("ZMIEŃ_NAZWĘ", { rename = true }, Modifier.weight(1f), bg = t.c.raised, fg = t.c.ink)
                    CyberButton("USUŃ_TALIĘ", { deleteDeck = true }, Modifier.weight(1f), bg = t.c.raised, fg = t.c.ink)
                }
            }
            item {
                Row(
                    Modifier
                        .fillMaxWidth()
                        .padding(start = 24.dp, end = 20.dp, top = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Bottom,
                ) {
                    Headline("Karty", size = 24)
                    MonoLabel("/CARDS [%02d]".format(ui.cards.size), decorative = true)
                }
            }
            if (ui.cards.isEmpty()) {
                item {
                    Panel(Modifier.padding(horizontal = 20.dp).fillMaxWidth()) {
                        MonoLabel("_EMPTY", color = t.c.primary, bold = true)
                        Text("Ta talia jest pusta. Dodaj pierwszą fiszkę przyciskiem +.", fontSize = 15.sp)
                    }
                }
            }
            items(ui.cards, key = { it.id }) { card ->
                CardRow(
                    card = card,
                    due = card.dueAtMillis <= ui.now,
                    onClick = { onEditCard(card.id) },
                    onDelete = { deleteCard = card },
                )
            }
        }

        // FAB: nowa fiszka w tej talii
        Box(
            Modifier
                .align(Alignment.BottomEnd)
                .padding(end = 20.dp, bottom = 24.dp)
                .size(58.dp)
                .clip(t.shape(14.dp))
                .background(t.accent)
                .clickable(role = Role.Button) { onAddCard(deck.id) }
                .semantics { contentDescription = "Dodaj fiszkę do talii" },
            contentAlignment = Alignment.Center,
        ) {
            Text("+", color = t.onAccent, fontSize = 30.sp, fontWeight = FontWeight.Bold)
        }
    }

    if (rename) {
        DeckFormDialog(
            title = "Zmień nazwę",
            initialName = deck.name,
            initialShort = deck.short,
            confirm = "ZAPISZ",
            onConfirm = { name, short ->
                vm.rename(name, short)
                rename = false
            },
            onDismiss = { rename = false },
        )
    }
    if (deleteDeck) {
        ConfirmDialog(
            title = "Usunąć talię?",
            message = "Talia „${deck.name}” i ${kart(ui.cards.size)} zostaną usunięte. Historia powtórek w statystykach zostaje.",
            confirm = "USUŃ",
            onConfirm = {
                deleteDeck = false
                vm.deleteDeck() // powrót robi LaunchedEffect, gdy talia zniknie z bazy
            },
            onDismiss = { deleteDeck = false },
        )
    }
    deleteCard?.let { card ->
        ConfirmDialog(
            title = "Usunąć fiszkę?",
            message = "„${card.front}” → „${card.back}”",
            confirm = "USUŃ",
            onConfirm = {
                vm.deleteCard(card)
                deleteCard = null
            },
            onDismiss = { deleteCard = null },
        )
    }
}

@Composable
private fun CardRow(card: Card, due: Boolean, onClick: () -> Unit, onDelete: () -> Unit) {
    val t = Fiszki.t
    Panel(
        Modifier
            .padding(horizontal = 20.dp)
            .fillMaxWidth(),
        padding = PaddingValues(start = 14.dp, top = 10.dp, bottom = 10.dp, end = 0.dp),
        onClick = onClick,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(
                    card.front.uppercase(),
                    fontFamily = Fonts.Display,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 19.sp,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(card.back, color = t.c.muted, fontSize = 14.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
                Spacer(Modifier.height(4.dp))
                MonoLabel(
                    when {
                        card.reps == 0 && card.intervalDays == 0 && due -> "NOWA // DO POWTÓRKI"
                        due -> "DO POWTÓRKI // INT ${card.intervalDays}D"
                        else -> "INT ${card.intervalDays}D"
                    },
                    color = if (due) t.accent else t.c.muted,
                    size = 10,
                    bold = due,
                )
            }
            Box(
                Modifier
                    .size(48.dp)
                    .clickable(role = Role.Button, onClick = onDelete)
                    .semantics { contentDescription = "Usuń fiszkę ${card.front}" },
                contentAlignment = Alignment.Center,
            ) {
                val ink = t.c.muted
                Canvas(Modifier.size(14.dp)) {
                    val s = 2.dp.toPx()
                    drawLine(ink, Offset(0f, 0f), Offset(size.width, size.height), s)
                    drawLine(ink, Offset(size.width, 0f), Offset(0f, size.height), s)
                }
            }
        }
    }
}

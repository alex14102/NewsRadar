package pl.fiszki.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import pl.fiszki.app.data.Repository
import pl.fiszki.app.ui.components.CyberButton
import pl.fiszki.app.ui.components.CyberField
import pl.fiszki.app.ui.components.CyberToggle
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.TopBar
import pl.fiszki.app.ui.theme.Fiszki

@Composable
fun AddCardScreen(repo: Repository, onDone: () -> Unit) {
    val t = Fiszki.t
    var deckId by remember { mutableLongStateOf(repo.decks.first().id) }
    var front by remember { mutableStateOf("") }
    var back by remember { mutableStateOf("") }
    var example by remember { mutableStateOf("") }
    var reversed by remember { mutableStateOf(true) }
    val valid = front.isNotBlank() && back.isNotBlank()

    Column(
        Modifier
            .fillMaxSize()
            .imePadding()
    ) {
        TopBar(title = "Nowa fiszka", sub = "CARD.NEW()", onBack = onDone, backLabel = "Zamknij")
        Column(
            Modifier
                .weight(1f)
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                MonoLabel("> TALIA", color = t.accent)
                Row(
                    Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    repo.decks.forEach { d ->
                        val sel = d.id == deckId
                        Box(
                            Modifier
                                .heightIn(min = 44.dp)
                                .clip(t.shape(8.dp))
                                .background(if (sel) t.c.primary else t.c.raised)
                                .selectable(selected = sel, role = Role.RadioButton) { deckId = d.id }
                                .padding(horizontal = 16.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            MonoLabel(d.short, color = if (sel) t.c.onPrimary else t.c.ink, size = 12, bold = true)
                        }
                    }
                }
            }
            CyberField("> PRZÓD", front, { front = it })
            CyberField("> TYŁ", back, { back = it })
            CyberField("> PRZYKŁAD [OPCJONALNIE]", example, { example = it }, big = false, minLines = 3)
            Column {
                CyberToggle("Dodaj też odwróconą", "TYŁ → PRZÓD", reversed) { reversed = it }
            }
        }
        Row(
            Modifier.padding(20.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            CyberButton("ANULUJ", onDone, Modifier.weight(1f), bg = t.c.raised, fg = t.c.ink)
            CyberButton(
                "ZAPISZ_FISZKĘ",
                onClick = {
                    repo.addCard(deckId, front.trim(), back.trim(), example.trim(), reversed)
                    onDone()
                },
                modifier = Modifier.weight(2f),
                enabled = valid,
            )
        }
    }
}

package pl.fiszki.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import pl.fiszki.app.ui.components.CyberButton
import pl.fiszki.app.ui.components.CyberField
import pl.fiszki.app.ui.components.CyberToggle
import pl.fiszki.app.ui.components.MonoLabel
import pl.fiszki.app.ui.components.Panel
import pl.fiszki.app.ui.components.TopBar
import pl.fiszki.app.ui.theme.Fiszki
import pl.fiszki.app.ui.viewmodel.CardEditorViewModel

/** Nowa fiszka albo edycja istniejącej (zależnie od vm.isEdit). */
@Composable
fun AddCardScreen(vm: CardEditorViewModel, onDone: () -> Unit) {
    val t = Fiszki.t
    val decks by vm.decks.collectAsStateWithLifecycle()
    LaunchedEffect(decks) { decks?.let(vm::ensureDeck) }

    Column(
        Modifier
            .fillMaxSize()
            .imePadding()
    ) {
        TopBar(
            title = if (vm.isEdit) "Edycja fiszki" else "Nowa fiszka",
            sub = if (vm.isEdit) "CARD.EDIT()" else "CARD.NEW()",
            onBack = onDone,
            backLabel = "Zamknij",
        )
        val list = decks
        if (list != null && list.isEmpty()) {
            Panel(
                Modifier
                    .padding(20.dp)
                    .fillMaxWidth()
            ) {
                MonoLabel("_NO_DECKS", color = t.c.primary, bold = true)
                Text("Najpierw utwórz talię na ekranie TALIE (+ NOWA_TALIA).", fontSize = 15.sp)
            }
            CyberButton("WRÓĆ", onDone, Modifier.fillMaxWidth().padding(20.dp))
            return@Column
        }
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
                    list.orEmpty().forEach { d ->
                        val sel = d.id == vm.deckId
                        Box(
                            Modifier
                                .heightIn(min = 48.dp)
                                .clip(t.shape(8.dp))
                                .background(if (sel) t.c.primary else t.c.raised)
                                .selectable(selected = sel, role = Role.RadioButton) { vm.deckId = d.id }
                                .padding(horizontal = 16.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            MonoLabel(d.short, color = if (sel) t.c.onPrimary else t.c.ink, size = 12, bold = true)
                        }
                    }
                }
            }
            if (vm.ready) {
                CyberField("> PRZÓD", vm.front, { vm.front = it })
                CyberField("> TYŁ", vm.back, { vm.back = it })
                CyberField("> WYMOWA [OPCJONALNIE]", vm.ipa, { vm.ipa = it }, big = false)
                CyberField("> PRZYKŁAD [OPCJONALNIE]", vm.example, { vm.example = it }, big = false, minLines = 3)
                if (!vm.isEdit) {
                    Column {
                        CyberToggle("Dodaj też odwróconą", "TYŁ → PRZÓD", vm.reversed) { vm.reversed = it }
                    }
                }
            }
        }
        Row(
            Modifier.padding(20.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            CyberButton("ANULUJ", onDone, Modifier.weight(1f), bg = t.c.raised, fg = t.c.ink)
            CyberButton(
                if (vm.isEdit) "ZAPISZ_ZMIANY" else "ZAPISZ_FISZKĘ",
                onClick = { vm.save(onDone) },
                modifier = Modifier.weight(2f),
                enabled = vm.ready && vm.valid,
            )
        }
    }
}

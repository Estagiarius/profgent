# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
# Importa a biblioteca 'asyncio' para trabalhar com programação assíncrona (coroutines).
import asyncio


def run_async_task(coro, loop, queue, callback):
    """
    Despacha uma corrotina para o loop asyncio sem bloquear a thread da UI e sem criar
    threads extras por chamada. Ao concluir, enfileira o callback com o resultado ou
    a exceção na fila thread-safe consumida pela thread principal.

    :param coro: Coroutine assíncrona a ser executada no loop de eventos.
    :param loop: Loop de eventos asyncio onde a coroutine será executada.
    :param queue: Fila thread-safe que armazena o callback e o resultado (ou exceção).
    :param callback: Função a ser chamada na thread principal com o resultado ou exceção.
    """
    future = asyncio.run_coroutine_threadsafe(coro, loop)

    def _on_done(done_future):
        try:
            result = done_future.result()
            queue.put((callback, (result,)))
        except Exception as e:
            queue.put((callback, (e,)))

    future.add_done_callback(_on_done)
    return future

# Importa a biblioteca 'asyncio' para trabalhar com programação assíncrona (coroutines).
import asyncio
# Importa a biblioteca 'threading' para executar operações em threads separadas, em segundo plano.
import threading

# Define a função que executa uma tarefa assíncrona a partir de um contexto síncrono (como a UI).
def run_async_task(coro, loop, queue, callback):
    """
    Executa uma coroutine em uma thread de segundo plano no loop de eventos principal da aplicação,
    e enfileira um callback para ser executado na thread principal da UI após a conclusão.

    Esta é a maneira padrão e sem bloqueio de executar tarefas assíncronas a partir da UI nesta aplicação.

    Args:
        coro: A coroutine (função async) a ser executada.
        loop: O loop de eventos asyncio principal da aplicação.
        queue: A fila thread-safe para atualizações da UI.
        callback: A função a ser chamada na thread principal com o resultado da coroutine.
    """
    # Define uma função interna (wrapper) que será o alvo da nossa thread de segundo plano.
    def task_wrapper():
        # Esta função é executada em uma thread separada.
        # Ela submete a coroutine ao loop de eventos principal e aguarda pelo resultado.
        # `run_coroutine_threadsafe` é a forma segura de interagir com um loop asyncio de outra thread.
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            # `future.result()` é uma chamada bloqueante, mas bloqueia APENAS esta thread de segundo plano,
            # não a thread principal da UI, que continua responsiva.
            result = future.result()
            # Assim que o resultado estiver pronto, coloca ele e a função de callback na fila thread-safe.
            # A thread principal irá ler desta fila para executar o callback.
            queue.put((callback, (result,)))
        except Exception as e:
            # Se a tarefa assíncrona levantar uma exceção, a exceção é enfileirada
            # para que o callback na thread principal possa tratá-la (ex: mostrar uma mensagem de erro).
            queue.put((callback, (e,)))

    # Cria a thread de segundo plano para gerenciar a tarefa assíncrona.
    thread = threading.Thread(target=task_wrapper)
    # Define a thread como 'daemon', o que significa que ela não impedirá o programa de fechar.
    thread.daemon = True
    # Inicia a execução da thread.
    thread.start()

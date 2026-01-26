import os
import time
from playwright.sync_api import Playwright, sync_playwright, expect
from dotenv import load_dotenv

# --- Configuração Inicial ---
load_dotenv()
USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
# PERIODO = os.getenv("21/01/2026")

# --- LISTA DE TÍTULOS ---
raw_titulos = """
000000046193
000000046367
000000047536
000000047633
000000047703
000000047924
000000048508
000000048817
000000049050
000000049083
000000049088
000000049113
000000049138
000000049139
000000049140
000000049141
000000049142
000000049144
000000049354
000000049697
000000049806
000000050768
000000050820




""" 

# TRATAMENTO DA LISTA:
lista_titulos = [t.strip() for t in raw_titulos.split('\n') if t.strip()]

input("⚠️ ATENÇÃO: MODO PRODUÇÃO (VAI SALVAR). Pressione Enter para iniciar...")
print(">>> Script Iniciado. Preparando ambiente...")

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(60000)

    # --- LISTAS PARA O RELATÓRIO FINAL ---
    lista_sucesso = []
    lista_erro = []

    try:
        # --- Navegação e Login ---
        print("--- Etapa: Login e Acesso ---")
        page.goto("https://selbetti174877.protheus.cloudtotvs.com.br:4010/webapp/")
        page.get_by_role("group", name="Ambiente no servidor").get_by_role("combobox").select_option("CS86R7_PROD")
        page.get_by_role("button", name="Ok").click()

        time.sleep(6)
        frame = page.frame_locator("iframe").first
        
        print("Preenchendo credenciais...")
        frame.get_by_role("textbox", name="Insira seu usuário").click()
        frame.get_by_role("textbox", name="Insira seu usuário").fill(USUARIO)
        frame.get_by_role("textbox", name="Insira sua senha").click()
        frame.get_by_role("textbox", name="Insira sua senha").fill(SENHA)
        frame.get_by_role("button", name="Entrar").click()
        # Clique de segurança duplo no Entrar (mantido)
        frame.get_by_role("button", name="Entrar").click()

        # Troca de Módulo
        print("Trocando Módulo e Data Base...")
        page.get_by_role("button", name="Trocar módulo").click()
        try:
            page.locator("#COMP4507").get_by_role("textbox").click()
            time.sleep(2)
            page.locator("#COMP4507").get_by_role("textbox").fill("23/01/2026")
            time.sleep(2)
            page.get_by_role("button", name="Confirmar").click()
        except:
            print("(!) Aviso: ID da data mudou (continuando).")
        
        time.sleep(3)
        
        # --- Acessa Favoritos e Data ---
        print("Acessando Favoritos...")
        page.wait_for_selector("text=Favoritos")
        page.get_by_text("Favoritos", exact=True).click()
        time.sleep(2)
        
        print("Entrando na rotina Contas a Receber...")
        page.get_by_title("Funções Contas a Receber", exact=True).click()
        
        # Confirmar Parâmetros Iniciais
        print("Confirmando parâmetros iniciais...")
        time.sleep(2)
        page.get_by_role("button", name="Confirmar").is_visible(timeout=10000)
        page.get_by_role("button", name="Confirmar").click()
        
        print("Aguardando carregamento da tela principal (15s)...")
        time.sleep(15) 
        
        # Aguarda a dialogo aparecer e cancela (mantido)
        if page.get_by_role("button", name="Cancelar").is_visible():
            page.get_by_role("button", name="Cancelar").click()
        
        print("Aguardando estabilização (10s)...")
        time.sleep(10) 
        

        # --- INÍCIO DO LAÇO ---
        total_titulos = len(lista_titulos)
        print(f"\n>>> INICIANDO PROCESSAMENTO DE {total_titulos} TÍTULOS <<<\n")

        for i, titulo in enumerate(lista_titulos):
            print(f"{'='*50}")
            print(f"ITEM {i+1}/{total_titulos} --> Processando Título: {titulo}")
            print(f"{'='*50}")
            
            try:
                # 1. FILTRAR 
                print("   [1] Abrindo Filtro...")
                
                menu_filtro_abriu = False
                
                # Tenta clicar no filtro até 3 vezes
                for tentativa in range(3):
                    try:
                        page.get_by_role("button", name="Filtrar").click()
                        time.sleep(2) # Espera a animação
                        
                        if page.get_by_role("button", name="Aplicar filtros selecionados").is_visible():
                            menu_filtro_abriu = True
                            break 
                        else:
                            print(f"       (!) Clique falhou. Tentando novamente ({tentativa+2}/3)...")
                            time.sleep(1)
                    except:
                        pass

                if not menu_filtro_abriu:
                    raise Exception("Menu de filtro não abriu após 3 tentativas.")
                
                # APLICAR 
                print("   [2] Aplicando seleção inicial do filtro...")
                page.get_by_role("button", name="Aplicar filtros selecionados").click()
                time.sleep(0.5)
                
                # Avança o banco
                print("   [2.5] Clicando em Avançar...")
                page.get_by_role("button", name="Avançar").click()
                time.sleep(0.5)

                # 2. DIGITAR O TÍTULO
                print(f"   [3] Preenchendo campo de texto com: {titulo}")
                time.sleep(2)
                
                # Seletor que funcionou
                page.get_by_title("Filtro através de perguntas").get_by_role("textbox").fill(titulo)

                time.sleep(1)
                
                print("       Preenchimento OK.")

                # 2.1. Confirmar filtro
                print("   [4] Confirmando filtro...")
                page.get_by_role("button", name="Confirmar").click()
                
                print("       Aguardando grid atualizar...")
                time.sleep(3) 
                
                print("       Aguardando loader do sistema...")
                try:
                    # Espera até 50s para o elemento de carregamento desaparecer
                    page.locator("#COMP7505").wait_for(state="hidden", timeout=50000)
                except:
                    print("       (Aviso: Loader não detectado ou timeout. Seguindo...)")

                time.sleep(4)
                
                # 3. Abrir tela de baixa
                print("   [5] Abrindo tela de Baixa...")
                page.get_by_role("button", name="Outras Ações").click()
                time.sleep(0.8)
                
                page.get_by_text("Baixas", exact=True).click()
                time.sleep(0.8)
                
                page.get_by_text("Baixar", exact=True).click()
                time.sleep(6)
                
                # 3. PREENCHER MOTIVO
                print("   [6] Selecionando Motivo da baixa...")
                
                page.locator("#COMP6029").click()
                page.keyboard.press("ArrowDown")
                page.keyboard.press("ArrowDown")   
                page.keyboard.press("Enter")
                time.sleep(0.7)
                
                
                print("       Aguardando preenchimento (5s)...")
                time.sleep(7)
                       
                # --- AÇÃO REAL: SALVAR ---
                print("   [7] SALVANDO A BAIXA...")
                page.get_by_role("button", name="Salvar").click()
                
                # Verifica confirmação extra ("Sim")
                time.sleep(2)
                # if page.get_by_role("button", name="Sim").is_visible():
                #      print("       Confirmando 'Sim'...")
                #      page.get_by_role("button", name="Sim").click()
                
                print(f"   [SUCESSO] Baixa finalizada para: {titulo}")
                
                # Registra sucesso
                lista_sucesso.append(titulo)
                
                time.sleep(7)
                print(f"--> Fim do ciclo para o título {titulo}.\n")

            except Exception as e_titulo:
                print(f"   [ERRO] Falha ao processar título {titulo}: {e_titulo}")
                
                # Registra erro
                lista_erro.append(f"{titulo} | Erro: {str(e_titulo)[:50]}")

                # Se der erro, tenta cancelar janelas abertas e vai pro próximo
                try:
                    if page.get_by_role("button", name="Cancelar").is_visible():
                        print("       Tentando fechar janelas de erro...")
                        page.get_by_role("button", name="Cancelar").click()
                except:
                    pass
                continue

        # --- RELATÓRIO FINAL ---
        print("\n" + "#"*60)
        print("RELATÓRIO FINAL DE EXECUÇÃO")
        print("#"*60)
        print(f"Total: {total_titulos} | Sucessos: {len(lista_sucesso)} | Falhas: {len(lista_erro)}")
        print("-" * 60)
        
        if len(lista_sucesso) > 0:
            print("\n✅ SUCESSOS:")
            for t in lista_sucesso:
                print(f"   -> {t}")
        
        if len(lista_erro) > 0:
            print("\n❌ ERROS:")
            for erro in lista_erro:
                print(f"   -> {erro}")
        
        print("#"*60 + "\n")
        
        # Mantém aberto pra você ver o relatório
        page.pause()

    except Exception as e:
        print(f"Erro Crítico Geral: {e}")
    
    finally:
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
#!/usr/bin/env python3
"""
Background Remover - Versão Refinada
====================================

Compatível com todas as versões do rembg, com ajustes para melhor qualidade.
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    try:
        import rembg
        from PIL import Image
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install rembg pillow onnxruntime")
        return False

def is_valid_image(file_path):
    """Verifica se um arquivo é uma imagem válida."""
    try:
        from PIL import Image
        if os.path.getsize(file_path) < 100:
            return False
        with Image.open(file_path) as img:
            img.verify()
            return True
    except Exception:
        return False

def remove_background_high_quality(input_path, output_path, model_name='u2net', alpha_matting=True):
    """
    Remove o fundo de uma imagem com mais qualidade.
    
    Args:
        input_path (str): Caminho da imagem de entrada
        output_path (str): Caminho de saída
        model_name (str): Modelo do rembg (padrão: u2net)
        alpha_matting (bool): Ativar alpha matting para melhorar contornos em cabelos/pelagem
        
    Returns:
        bool
    """
    try:
        import rembg
        from rembg import new_session, remove
        from PIL import Image
        import io

        if not os.path.exists(input_path):
            print(f"❌ Arquivo não encontrado: {input_path}")
            return False

        if not is_valid_image(input_path):
            print(f"❌ Arquivo não é uma imagem válida: {input_path}")
            return False

        print(f"🔄 Processando com qualidade: {input_path}")

        # Criar uma sessão com o modelo desejado
        session = new_session(model_name)

        # Abrir imagem original no modo correto
        with Image.open(input_path) as input_image:
            # Sempre converter para RGBA antes de remover o fundo (mantém canal alfa)
            input_image = input_image.convert("RGBA")

            # Converter imagem em bytes para a função remove
            img_bytes = io.BytesIO()
            input_image.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()

            # Remover fundo com a session otimizada
            output_bytes = remove(
                img_bytes, session=session,
                alpha_matting=alpha_matting,  # melhora contorno, mais lento
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )

            # Converter resultado de volta em imagem PIL
            output_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

            # Criar diretório se necessário
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Salvar com compressão e qualidade máxima
            output_image.save(output_path, 'PNG', optimize=True)

        print(f"✅ Salvo: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        return False

def process_directory_high_quality(input_dir, output_dir):
    """Processa todas as imagens do diretório com alta qualidade."""
    if not os.path.exists(input_dir):
        print(f"❌ Diretório não encontrado: {input_dir}")
        return 0, 0

    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

    image_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if Path(file).suffix.lower() in supported_formats:
                image_files.append(os.path.join(root, file))

    if not image_files:
        print(f"❌ Nenhuma imagem encontrada em: {input_dir}")
        return 0, 0

    print(f"📸 Encontradas {len(image_files)} imagens")

    success_count = 0
    fail_count = 0

    for i, img_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}]", end=" ")

        rel_path = os.path.relpath(img_file, input_dir)
        output_file = os.path.join(output_dir, rel_path)
        output_file = os.path.splitext(output_file)[0] + '_sem_fundo.png'

        if remove_background_high_quality(img_file, output_file):
            success_count += 1
        else:
            fail_count += 1

    return success_count, fail_count

def main():
    """Função principal com interface simples."""
    print("🎨 Removedor de Fundo de Imagens (Alta Qualidade)")
    print("=" * 45)

    if not check_dependencies():
        return

    print("\nEscolha uma opção:")
    print("1. Processar uma imagem (Alta Qualidade)")
    print("2. Processar um diretório (Alta Qualidade)")
    print("3. Sair")

    while True:
        try:
            choice = input("\nOpção (1-3): ").strip()

            if choice == '1':
                input_path = input("📁 Caminho da imagem de entrada: ").strip()
                if not input_path:
                    print("❌ Caminho não pode estar vazio!")
                    continue

                output_path = input("💾 Caminho de saída (Enter para automático): ").strip()
                if not output_path:
                    base_name = os.path.splitext(input_path)[0]
                    output_path = f"{base_name}_sem_fundo.png"

                success = remove_background_high_quality(input_path, output_path)
                if success:
                    print(f"🎉 Sucesso! Imagem salva em: {output_path}")
                else:
                    print("😞 Falha no processamento")
                break

            elif choice == '2':
                input_dir = input("📁 Diretório de entrada: ").strip()
                if not input_dir:
                    print("❌ Diretório não pode estar vazio!")
                    continue

                output_dir = input("💾 Diretório de saída (Enter para './processadas'): ").strip()
                if not output_dir:
                    output_dir = "./processadas"

                success_count, fail_count = process_directory_high_quality(input_dir, output_dir)

                total = success_count + fail_count
                print(f"\n📊 Processamento concluído:")
                print(f"✅ Sucessos: {success_count}/{total}")
                print(f"❌ Falhas: {fail_count}/{total}")

                if success_count > 0:
                    print(f"🎉 Imagens processadas salvas em: {output_dir}")
                break

            elif choice == '3':
                print("👋 Até logo!")
                break

            else:
                print("❌ Opção inválida! Digite 1, 2 ou 3.")

        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()

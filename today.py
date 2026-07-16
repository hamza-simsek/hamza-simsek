import os
import re
import requests

# GitHub API'den istatistikleri çekme fonksiyonu
def get_github_stats(username, token):
    headers = {'Authorization': f'token {token}'}
    
    # Kullanıcı genel bilgileri
    user_url = f'https://api.github.com/users/{username}'
    user_data = requests.get(user_url, headers=headers).json()
    
    followers = user_data.get('followers', 0)
    public_repos = user_data.get('public_repos', 0)
    
    # Yıldız (Stars) ve Commits sayıları için tüm repoları tarayalım
    repos_url = f'https://api.github.com/users/{username}/repos?per_page=100'
    repos_data = requests.get(repos_url, headers=headers).json()
    
    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos_data if isinstance(repo, dict))
    
    # Varsayılan değerleri güncellemek için (API limitlerine takılma durumunda koruma)
    return {
        'repos': public_repos,
        'stars': total_stars,
        'followers': followers
    }

def update_svg(file_path, stats):
    if not os.path.exists(file_path):
        print(f"Hata: {file_path} bulunamadı!")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # SVG içindeki istatistik kısımlarını düzenli ifadelerle güncelleme
    # Repos
    content = re.sub(r'(<tspan class="key">Repos</tspan>:<tspan class="cc"> \.\.\.\. </tspan><tspan class="value">)\d+(</tspan>)', f'\\1{stats["repos"]}\\2', content)
    # Stars
    content = re.sub(r'(<tspan class="key">Stars</tspan>:<tspan class="cc"> \.\.\.\.\.\.\.\.\.\.\. </tspan><tspan class="value">)\d+(</tspan>)', f'\\1{stats["stars"]}\\2', content)
    # Followers
    content = re.sub(r'(<tspan class="key">Followers</tspan>:<tspan class="cc"> \.\.\.\.\.\.\. </tspan><tspan class="value">)\d+(</tspan>)', f'\\1{stats["followers"]}\\2', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"{file_path} başarıyla güncellendi.")

if __name__ == '__main__':
    # GitHub Action çalışırken otomatik token alacak
    TOKEN = os.getenv('GP_TOKEN', os.getenv('GITHUB_TOKEN'))
    USERNAME = 'hamza-simsek'
    
    # Statik veriler dışında dinamik olanları API'den çek
    try:
        stats = get_github_stats(USERNAME, TOKEN)
    except Exception as e:
        print("API'den veri çekilemedi, varsayılan değerler kullanılıyor.", e)
        stats = {'repos': 15, 'stars': 12, 'followers': 15}
        
    update_svg('dark_mode.svg', stats)
    update_svg('light_mode.svg', stats)

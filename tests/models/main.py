import random
from app import db
import models


# db.session.add(models.WordList(word1="home", annotation1="sdfsdf", word2="Дом", annotation2="sdfsdf"))
# db.session.commit()

# words_to_add = [
#     {"word1": "to fly", "annotation1": "[flaɪ]", "word2": "летать", "annotation2": ""},
#     {"word1": "to swim", "annotation1": "[swɪm]", "word2": "плавать", "annotation2": ""},
#     {"word1": "to decide", "annotation1": "[dɪˈsaɪd]", "word2": "решать", "annotation2": ""},
#     {"word1": "to return", "annotation1": "[rɪˈtɜːn]", "word2": "возвращаться, возвращать", "annotation2": ""},
#     {"word1": "to hope", "annotation1": "[həʊp]", "word2": "надеяться", "annotation2": ""},
#     {"word1": "to explain", "annotation1": "[ɪkˈspleɪn]", "word2": "объяснять", "annotation2": ""},
#     {"word1": "to propose", "annotation1": "[prəˈpəʊz]", "word2": "предлагать", "annotation2": ""},
#     {"word1": "to develop", "annotation1": "[dɪˈveləp]", "word2": "развивать", "annotation2": ""},
#     {"word1": "to support", "annotation1": "[səˈpɔːt]", "word2": "поддерживать", "annotation2": ""},
#     {"word1": "to dance", "annotation1": "[dɑːns]", "word2": "танцевать", "annotation2": ""},
#     {"word1": "to draw", "annotation1": "[drɔː]", "word2": "рисовать", "annotation2": ""},
#     {"word1": "to book", "annotation1": "[bʊk]", "word2": "бронировать", "annotation2": ""},
#     {"word1": "to be afraid", "annotation1": "[bi əˈfreɪd]", "word2": "бояться", "annotation2": ""},
#     {"word1": "to agree", "annotation1": "[əˈɡriː]", "word2": "соглашаться", "annotation2": ""},
#     {"word1": "to check up", "annotation1": "[tʃek ʌp]", "word2": "проверять", "annotation2": ""},
#     {"word1": "to delete", "annotation1": "[dɪˈliːt]", "word2": "удалять", "annotation2": ""},
#     {"word1": "to choose", "annotation1": "[tʃuːz]", "word2": "выбирать", "annotation2": ""},
#     {"word1": "to catch", "annotation1": "[kætʃ]", "word2": "ловить", "annotation2": ""},
#     {"word1": "to ask", "annotation1": "[ɑːsk]", "word2": "спрашивать", "annotation2": ""},
#     {"word1": "to answer", "annotation1": "[ˈɑːnsə(r)]", "word2": "отвечать", "annotation2": ""},
#     {"word1": "to hesitate", "annotation1": "[ˈhezɪteɪt]", "word2": "сомневаться", "annotation2": ""}
# ]

# for word_data in words_to_add:
#     db.session.add(models.WordList(**word_data))

# # Committing the changes to the database
# db.session.commit()


def training(user_id, flag=True):
    words_list = models.WordList.query.all()
    success = 0
    invalid = 0
    print("Щоб вийти напишіть 8")
    while True:
        word = random.choice(words_list)
        if flag:
            print(word.word1, word.annotation1, sep=" ")
            user_word = input("Enter translite ")
            if user_word == word.word2:
                success += 1
            elif user_word == "8":
                break
            else:
                invalid += 1

    user = models.UsersTraining.query.all()
    if user:
        training_id = user[-1].training_id + 1
    else:
        training_id = 1
    db.session.add(models.UsersTraining(
        user_id=user_id, success_words=success, invalid_words=invalid, training_id=training_id))
    db.session.commit()


def create_user(name, user_id):
    db.session.add(models.Users(user_id=user_id, user_name=name))
    db.session.commit()


# create_user("Misha", "2354345354")

user = models.Users.query.filter_by(user_name="Misha").first()
if user:
    training(user.user_id)

    training = models.UsersTraining.query.all()

    user = models.Users.query.filter_by(user_id=user.user_id).first()
    print("Name ", user.user_name)
    print("Number training ", training[-1].training_id)

else:
    print("not found")

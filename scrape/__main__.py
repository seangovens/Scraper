import sys
import time
import random
import pickle
from scrape.rt_scraper import RTScraper
from scrape.entities.person import People


def weight_quad(items, exp):
    if len(items) < 1:
        return 0
    res = 0.0
    t_w = 0.0
    for i in range(len(items)):
        w = -(i / len(items))**exp + 1
        res += w * items[i]
        t_w += w
    return res / t_w


def weight_linear(items):
    if len(items) < 1:
        return 0
    res = 0.0
    for i in range(len(items)):
        res += (len(items) - i)*items[i]
    return res / (len(items) * (len(items) + 1) / 2)


def weight_mean(items):
    if len(items) < 1:
        return 0
    return sum(items) / len(items)


def lookup(s, names, job, dic):
    people_scores = []
    for name in names:
        try:
            if name not in dic:
                time.sleep(random.randrange(2, 5))
                p = s.get_person(name, job)
                scores = p.get_scores(job_specific=True)
                dic[name] = scores
            else:
                scores = dic[name]

            print("scores {}: {}".format(name, scores))
            if len(scores) > 0:
                people_scores.append(weight_linear(scores))
        except AttributeError:
            pass
    return [weight_mean(people_scores), weight_linear(people_scores),
            weight_quad(people_scores, 2)]


def write_headings(out):
    out.write("title,director mean, director linear, director quad,"
              "writer mean, writer linear, writer quad,"
              "actor mean, actor linear, actor quad,"
              "rating, action adventure, drama, scifi fantasy, animation,"
              "comedy, kids family, art international, mystery suspense,"
              "romance, documentary, horror\n")
    return


# def main():
#     s = RTScraper()
#     c = s.get_person("ang_lee", People.DIRECTOR)
#     print(c.get_scores())


def dump(director_dic, writer_dic, actor_dic, movie_dic):
    print("Dumping to file...")
    director_file = open("directors", "wb")
    writer_file = open("writers", "wb")
    actor_file = open("actors", "wb")
    movie_file = open("movies", "wb")
    pickle.dump(director_dic, director_file)
    pickle.dump(writer_dic, writer_file)
    pickle.dump(actor_dic, actor_file)
    pickle.dump(movie_dic, movie_file)
    director_file.close()
    writer_file.close()
    actor_file.close()
    movie_file.close()


def main():
    s = RTScraper()

    with open(sys.argv[1], "r") as movies:
        director_file = open("directors", "rb")
        writer_file = open("writers", "rb")
        actor_file = open("actors", "rb")
        movie_file = open("movies", "rb")
        try:
            director_dic = pickle.load(director_file)
            writer_dic = pickle.load(writer_file)
            actor_dic = pickle.load(actor_file)
            movie_dic = pickle.load(movie_file)
        except EOFError:
            director_dic = {}
            writer_dic = {}
            actor_dic = {}
            movie_dic = {}
        director_file.close()
        writer_file.close()
        actor_file.close()
        movie_file.close()

        for movie in movies:
            try:
                if movie not in movie_dic:
                    m = s.get_movie(movie)
                    score = m.get_score()
                    if score >= 0:
                        ent = [movie.strip("\n")] \
                                + lookup(s, m.get_directors(), People.DIRECTOR, director_dic) \
                                + lookup(s, m.get_writers(), People.WRITER, writer_dic) \
                                + lookup(s, m.get_actors(), People.ACTOR, actor_dic) \
                                + [m.get_rating().value] \
                                + m.genre_vector() + [score]
                        str_ent = [str(e) for e in ent]
                        out = open("out.csv", "a")
                        out.write(",".join(str_ent) + "\n")
                        out.close()
                        print("Wrote {} to file".format(movie))
                    else:
                        print("{} has no score".format(movie))
                    movie_dic[movie] = True
                    time.sleep(random.randrange(5, 20))
            except AttributeError:
                try:
                    movie_dic[movie] = True
                    time.sleep(random.randrange(2, 5))
                    print("Failed to get movie: {}".format(movie))
                except KeyboardInterrupt:
                    dump(director_dic, writer_dic, actor_dic, movie_dic)
            except KeyboardInterrupt:
                dump(director_dic, writer_dic, actor_dic, movie_dic)

if __name__ == "__main__":
    main()
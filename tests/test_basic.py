import pytest

from pygame import Rect

from pam.actor import Actor, ActorGroup
from pam.action import ActMove, ActRotate, ActColor, ActStop, Action
from pam.scene import Scene


# ---------------------------------- ACTOR ---------------------------------- #
@pytest.fixture()
def empty_actor():
    return Actor()


@pytest.fixture()
def normal_actor():
    a = Actor()
    a.act(ActMove, 1, (100, 200))
    a.act(ActRotate, 2, 90)
    a.act(ActMove, 0.5, (200, 100))
    return a


@pytest.fixture()
def busy_actor():
    actor = Actor()
    actor.act(ActStop, 2)
    actor.act(ActMove, 2, (100, 200))
    actor.act(ActRotate, 2, 90)
    return actor


def test_actor_init(empty_actor):
    assert len(empty_actor.actions) == 0
    assert empty_actor.rect.topleft == (0, 0)
    assert empty_actor.rect.width == 0
    assert empty_actor.rect.height == 0
    assert empty_actor.position == (0, 0)
    assert empty_actor.color == (255, 255, 255)


def test_actor_setup_states(empty_actor):
    empty_actor.position = (10, 10)
    empty_actor.color = (1, 2, 3)
    empty_actor.angle = 15

    start_state = empty_actor.state_at(0)
    assert start_state["position"] == (10, 10)
    assert start_state["color"] == (1, 2, 3)
    assert start_state["angle"] == 15


def test_actor_change_size(empty_actor):
    empty_actor.rect = (1, 2, 10, 20)
    assert empty_actor.rect.left == 1
    assert empty_actor.rect.top == 2
    assert empty_actor.rect.width == 10
    assert empty_actor.rect.height == 20
    assert empty_actor.image.get_width() == 10
    assert empty_actor.image.get_height() == 20


def test_actor_change_pos(empty_actor):
    empty_actor.rect = (1, 2, 3, 4)
    assert empty_actor.rect.topleft == (1, 2)
    assert empty_actor.position == (1, 2)

    empty_actor.position = (6, 7)
    assert empty_actor.rect.topleft == (6, 7)
    assert empty_actor.position == (6, 7)


def test_actor_add_action(empty_actor):
    empty_actor.act(ActStop, 2)
    empty_actor.act(ActMove, 1, (100, 200))
    empty_actor.act(ActRotate, 1, 90)

    assert len(empty_actor.actions) == 3
    assert empty_actor.actions[0].type == "ActStop"
    assert empty_actor.actions[0].duration == 2
    assert empty_actor.actions[0].dest == ""
    assert empty_actor.actions[1].type == "ActMove"
    assert empty_actor.actions[1].duration == 1
    assert empty_actor.actions[1].dest == (100, 200)
    assert empty_actor.actions[2].type == "ActRotate"
    assert empty_actor.actions[2].duration == 1
    assert empty_actor.actions[2].dest == 90


def test_actor_action_at(normal_actor):
    assert normal_actor.action_at(0).type == "ActMove"
    assert normal_actor.action_at(0.5).type == "ActMove"
    assert normal_actor.action_at(1).type == "ActRotate"
    assert normal_actor.action_at(1.5).type == "ActRotate"
    assert normal_actor.action_at(2).type == "ActRotate"
    assert normal_actor.action_at(2.5).type == "ActRotate"
    assert normal_actor.action_at(3).type == "ActMove"
    assert normal_actor.action_at(3.5).type == "ActStop"
    assert normal_actor.action_at(4).type == "ActStop"


def test_actor_color_change(empty_actor):

    empty_actor.act(ActColor, 2, (255, 0, 0))

    assert empty_actor.color == (255, 255, 255)
    empty_actor.update(0.0167)
    assert empty_actor.color == (255, 252.87075, 252.87075)
    empty_actor.update(1)
    assert empty_actor.color == (255, 127.5, 127.5)
    empty_actor.update(2)
    assert empty_actor.color == (255, 0, 0)
    empty_actor.update(3)
    assert empty_actor.color == (255, 0, 0)


def test_actor_move(empty_actor):

    empty_actor.act(ActMove, 2, (100, 200))

    # check if position changes with time
    assert empty_actor.position == (0, 0)
    empty_actor.update(0.0167)
    assert empty_actor.position == (0.835, 1.67)
    empty_actor.update(1)
    assert empty_actor.position == (50, 100)
    empty_actor.update(2)
    assert empty_actor.action_at(2).type == "ActStop"
    assert empty_actor.state_at(2)["position"] == (100, 200)
    assert empty_actor.position == (100, 200)
    empty_actor.update(3)
    assert empty_actor.position == (100, 200)


def test_actor_stop(empty_actor):

    assert empty_actor.state_at(0) == empty_actor.state_at(100)


def test_actor_add_action_type(empty_actor):

    class ActCustom(Action):

        def state_after(self, time_passed):
            return dict(self.start_state, custom_state=time_passed)

    empty_actor.act(ActCustom, 2, 0)
    assert empty_actor.action_at(0).type == "ActCustom"
    assert empty_actor.state_at(0)["custom_state"] == 0
    assert empty_actor.state_at(1)["custom_state"] == 1

    assert empty_actor.action_at(3).type == "ActStop"
    assert empty_actor.state_at(3)["custom_state"] == 2


# ---------------------------------- SCENE ---------------------------------- #
@pytest.fixture()
def basic_scene():
    return Scene(600, 400)


def test_scene_init(basic_scene):
    assert basic_scene.width == 600
    assert basic_scene.height == 400
    assert type(basic_scene.screen).__name__ == "Surface"


def test_scene_add_actors(basic_scene):
    actor1, actor2 = Actor(), Actor()
    basic_scene.add_actors(actor1)
    basic_scene.add_actors(actor2)
    assert len(basic_scene.groups["unnamed"]) == 2

    actorlist = [Actor(), Actor()]
    basic_scene.add_actors(actorlist)
    assert len(basic_scene.groups["unnamed"]) == 4

    basic_scene.add_actors(actorlist, groupname="mygroup")
    assert len(basic_scene.groups["unnamed"]) == 4
    assert len(basic_scene.groups["mygroup"]) == 2


def test_scene_add_actorgroup(basic_scene):
    actorgroup = ActorGroup()
    actorgroup.add(Actor(), Actor(), Actor())
    basic_scene.add_actorgroup(actorgroup, "mygroup1")
    assert len(basic_scene.groups["mygroup1"]) == 3

    # group 1 can be updated outside the actor
    actorgroup.add(Actor(), Actor(), Actor())
    assert len(basic_scene.groups["mygroup1"]) == 6

    # add actor in actor will affect the outer group as well
    basic_scene.add_actors(Actor(), groupname="mygroup1")
    assert len(actorgroup) == 7


def test_scene_update_fr(basic_scene):

    assert basic_scene.time == 0
    basic_scene.update()
    assert basic_scene.time >= 0.016


def test_scene_update_actor(basic_scene, busy_actor):
    basic_scene.add_actors(busy_actor)
    basic_scene.set_framerate(60)

    assert busy_actor.time == 0
    basic_scene.update()
    assert busy_actor.time >= 0.016


def test_scene_sync():
    a = Actor()
    b = Actor()
    c = Actor()
    s = Scene(1, 1)
    s.add_actors([a, b, c])

    a.act(ActMove, 1, (1, 1))
    b.act(ActColor, 2, (0, 0, 0))
    s.sync()

    assert a.actions.end_time == 2
    assert b.actions.end_time == 2
    assert c.actions.end_time == 2

    a.act(ActMove, 1, (1, 1))
    a.act(ActMove, 1, (1, 1))
    s.sync()

    assert a.actions.end_time == 4
    assert b.actions.end_time == 4
    assert c.actions.end_time == 4

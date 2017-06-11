if __name__ == "__main__":
    import sys
    from os.path import abspath as ap, dirname as dn

    sys.path.append(dn(dn(ap(__file__))))

    from kservices.main import app

    app.run(host="0.0.0.0", port=8110, workers=1, debug=True)
